import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage

# --- CONFIGURACAO INICIAL ---
load_dotenv()
CHAVE_API = os.environ.get("GOOGLE_API_KEY")

if not CHAVE_API:
    raise ValueError("ERRO: Chave GOOGLE_API_KEY nao encontrada no arquivo .env")

# Configura a biblioteca nativa do Google para diagnostico
genai.configure(api_key=CHAVE_API)

def validar_modelo_google():
    """
    Funcao de diagnostico: Lista os modelos disponiveis para sua chave
    e define qual usar para evitar erros 404.
    """
    print("--- DIAGNOSTICO DO GOOGLE GEMINI ---")
    try:
        modelos = list(genai.list_models())
        # Filtra apenas modelos que geram texto
        nomes_modelos = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods]
        print(f"Modelos disponiveis para sua chave: {nomes_modelos}")
        
        # Tenta usar o mais moderno primeiro
        if 'models/gemini-1.5-flash' in nomes_modelos:
            return 'gemini-1.5-flash'
        elif 'models/gemini-pro' in nomes_modelos:
            return 'gemini-pro'
        else:
            # Pega o primeiro disponivel como fallback e limpa o prefixo 'models/'
            if nomes_modelos:
                nome_limpo = nomes_modelos[0].replace('models/', '')
                return nome_limpo
            else:
                return 'gemini-1.5-flash' # Fallback final
            
    except Exception as e:
        print(f"AVISO: Nao foi possivel listar modelos ({e}). Tentando 'gemini-1.5-flash' padrao.")
        return 'gemini-1.5-flash'

def validar_modelo_embedding():
    """
    Funcao de diagnostico: Descobre dinamicamente qual modelo de embedding
    esta disponivel para a sua chave de API.
    """
    print("--- DIAGNOSTICO DO MODELO DE EMBEDDING ---")
    try:
        modelos = list(genai.list_models())
        # Filtra apenas modelos que suportam a criacao de embeddings
        modelos_embedding = [m.name for m in modelos if 'embedContent' in m.supported_generation_methods]
        print(f"Modelos de embedding disponiveis: {modelos_embedding}")
        
        # Tenta usar o mais moderno primeiro
        if 'models/text-embedding-004' in modelos_embedding:
            return 'models/text-embedding-004'
        elif 'models/embedding-001' in modelos_embedding:
            return 'models/embedding-001'
        elif modelos_embedding:
            # Retorna o primeiro da lista como fallback
            return modelos_embedding[0] 
        else:
            return 'models/text-embedding-004' # Fallback final cego
            
    except Exception as e:
        print(f"AVISO: Nao foi possivel listar modelos de embedding ({e}).")
        return 'models/text-embedding-004'

MODELO_EMBEDDING_SELECIONADO = validar_modelo_embedding()
print(f"--- EMBEDDING QUE SERA USADO: {MODELO_EMBEDDING_SELECIONADO} ---")

# --- DEFINICAO DO MODELO ---
# Executamos a validacao agora para saber qual modelo usar la embaixo
MODELO_SELECIONADO = validar_modelo_google()
print(f"--- MODELO QUE SERA USADO: {MODELO_SELECIONADO} ---")

# Caminhos das pastas
DIRETORIO_PDFS = "./data"
DIRETORIO_BANCO = "./vector_db"

# Variavel global para guardar o banco carregado na memoria
banco_vetorial_ativo = None

def carregar_e_processar_pdfs():
    """
    ETAPA 1: INGESTAO E CORTE (CHUNKING)
    Le todos os PDFs da pasta data e divide em pedacos menores.
    """
    print(f"--- 1. INICIANDO INGESTAO DE DOCUMENTOS EM: {DIRETORIO_PDFS} ---")
    
    # Garante que a pasta existe
    if not os.path.exists(DIRETORIO_PDFS):
        os.makedirs(DIRETORIO_PDFS)
        print(f"Pasta {DIRETORIO_PDFS} criada. Coloque os documentos internos nela.")
        return []

    todos_documentos = []
    arquivos = [f for f in os.listdir(DIRETORIO_PDFS) if f.endswith('.pdf')]
    
    if not arquivos:
        print("AVISO: Nenhum PDF encontrado na pasta data.")
        return []

    for arquivo in arquivos:
        caminho_completo = os.path.join(DIRETORIO_PDFS, arquivo)
        print(f"Lendo arquivo: {arquivo}...")
        try:
            loader = PyPDFLoader(caminho_completo)
            todos_documentos.extend(loader.load())
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")

    # Divisao em Chunks (Pedacos)
    divisor = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks_processados = divisor.split_documents(todos_documentos)
    
    print(f"--- Processamento concluido: {len(chunks_processados)} trechos criados. ---")
    return chunks_processados

def obter_banco_vetorial():
    """
    ETAPA 2: INDEXACAO (EMBEDDING)
    Transforma texto em numeros e salva no ChromaDB.
    """
    global banco_vetorial_ativo
    
    # Modelo de Embeddings do Google descoberto dinamicamente
    modelo_embedding = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDING_SELECIONADO, 
        google_api_key=CHAVE_API,
        task_type="retrieval_document"
    )
    
    # Singleton: Se ja carregamos na memoria, retorna direto
    if banco_vetorial_ativo:
        return banco_vetorial_ativo

    # Se o banco ja existe no disco, apenas carrega
    if os.path.exists(DIRETORIO_BANCO) and os.listdir(DIRETORIO_BANCO):
        print("--- 2. CARREGANDO BANCO VETORIAL EXISTENTE ---")
        banco_vetorial_ativo = Chroma(persist_directory=DIRETORIO_BANCO, embedding_function=modelo_embedding)
        return banco_vetorial_ativo
    
    # Se nao existe, cria do zero
    print("--- 2. CRIANDO NOVO BANCO VETORIAL (INDEXANDO)... ---")
    chunks = carregar_e_processar_pdfs()
    
    if not chunks:
        return None

    try:
        # 1. Inicializa o banco conectando ao diretorio vazio
        banco_vetorial_ativo = Chroma(
            embedding_function=modelo_embedding,
            persist_directory=DIRETORIO_BANCO
        )
        
        # 2. Divide os chunks em lotes de 80 (limite seguro abaixo de 100/min)
        tamanho_lote = 80
        for i in range(0, len(chunks), tamanho_lote):
            lote = chunks[i : i + tamanho_lote]
            print(f"Indexando lote de {i} a {i + len(lote)} (Total: {len(chunks)} trechos)...")
            
            # Adiciona o lote atual ao banco de dados
            banco_vetorial_ativo.add_documents(lote)
            
            # 3. Pausa de 65 segundos se ainda houver mais lotes para processar
            if i + tamanho_lote < len(chunks):
                print("Limite da API Gratuita: Pausando 65 segundos antes do proximo lote...")
                time.sleep(65)

        print("--- Banco salvo com sucesso! ---")
        return banco_vetorial_ativo
        
    except Exception as e:
        print(f"Erro ao criar embeddings: {e}")
        return None

def buscar_contexto(pergunta):
    """
    ETAPA 3: RECUPERACAO (RETRIEVAL)
    Busca os trechos mais parecidos com a pergunta.
    """
    banco = obter_banco_vetorial()
    if not banco:
        return "", []
    
    print(f"--- 3. BUSCANDO CONTEXTO PARA: '{pergunta}' ---")
    try:
        # k=4: Pega os 4 trechos mais relevantes
        resultados = banco.similarity_search(pergunta, k=4)
        
        texto_contexto = ""
        fontes = []
        
        for doc in resultados:
            # Limpa quebras de linha para economizar tokens
            conteudo_limpo = doc.page_content.replace("\n", " ")
            fonte_nome = os.path.basename(doc.metadata.get('source', 'Desconhecido'))
            pagina = doc.metadata.get('page', 0)
            
            texto_contexto += f"\n---\nFONTE: {fonte_nome} (Pag {pagina})\nCONTEUDO: {conteudo_limpo}\n"
            fontes.append(f"{fonte_nome} - Pag. {pagina}")
            
        return texto_contexto, fontes
    except Exception as e:
        print(f"Erro na busca: {e}")
        return "", []

def perguntar_ao_compliance_bot(pergunta, usar_rag=True):
    """
    ETAPA 4: GERACAO (GENERATION)
    Envia o contexto + pergunta para a IA gerar a resposta.
    """
    # Usamos o modelo validado dinamicamente no inicio do script
    llm = ChatGoogleGenerativeAI(model=MODELO_SELECIONADO, temperature=0.2)
    
    contexto = ""
    lista_fontes = []

    if usar_rag:
        contexto, lista_fontes = buscar_contexto(pergunta)
    
    if usar_rag and contexto:
        instrucao_sistema = """Voce e o Assistente de Governanca e Compliance do Itau.
        Sua funcao e auxiliar os colaboradores com base estritamente nas normas e politicas internas fornecidas.
        
        REGRAS:
        1. Use APENAS o contexto fornecido para basear sua resposta.
        2. Cite os documentos ou diretrizes mencionados no contexto.
        3. Se a resposta nao constar no contexto, diga: "Nao encontrei essa diretriz nos documentos internos analisados."
        4. Mantenha um tom profissional, orientativo e alinhado aos valores corporativos."""
        
        mensagem_usuario = f"DOCUMENTOS INTERNOS:\n{contexto}\n\nDUVIDA DO COLABORADOR: {pergunta}"
    else:
        # Modo Generico
        instrucao_sistema = "Voce e o Assistente de Governanca do Itau. Responda duvidas sobre etica corporativa com base em seu conhecimento geral, mas deixe claro que nao esta consultando as diretrizes oficiais do banco no momento."
        mensagem_usuario = pergunta

    print("--- 4. GERANDO RESPOSTA NA LLM... ---")
    try:
        # O Gemini prefere receber a mensagem formatada assim
        resposta = llm.invoke([
            SystemMessage(content=instrucao_sistema),
            HumanMessage(content=mensagem_usuario)
        ])
        
        return {
            "answer": resposta.content,
            "sources": lista_fontes
        }
    except Exception as e:
        return {
            "answer": f"Desculpe, erro ao processar resposta: {str(e)}",
            "sources": []
        }

obter_banco_vetorial()