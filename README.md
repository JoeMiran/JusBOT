# JusAI - Guia de Execucao

Este guia descreve os passos necessarios para configurar e rodar o projeto JusAI (Frontend e Backend) localmente.

## 1. Requisitos de Sistema
- Python 3.10 ou superior
- Node.js LTS (v18+)
- Git

## 2. Configuracao do Backend

1. Entre na pasta do backend:
cd backend

2. Crie o ambiente virtual:
python -m venv venv

3. Ative o ambiente virtual:
- Windows: venv\Scripts\activate
- Linux/Mac: source venv/bin/activate

4. Instale as dependencias:
pip install -r requirements.txt

5. Configure as credenciais:
- Crie um arquivo .env na raiz da pasta /backend
- Adicione sua chave do Google Gemini: GOOGLE_API_KEY="SUA_CHAVE_AQUI"

6. Prepare os documentos:
- Certifique-se de que seus arquivos PDF estao na pasta /backend/data

7. Inicie o servidor:
uvicorn main:app --reload

## 3. Configuracao do Frontend

1. Abra um novo terminal e entre na pasta do frontend:
cd frontend

2. Instale as dependencias:
npm install

3. Inicie a aplicacao:
npm run dev

4. Acesse o sistema:
- O terminal exibira um link (geralmente http://localhost:5173). Clique nele.

## 4. Notas Importantes para a Equipe

- O banco de dados vetorial (ChromaDB) e criado automaticamente na primeira execucao dentro da pasta /backend/vector_db.
- Caso voce adicione novos PDFs na pasta /data ou altere o modelo de embedding, voce DEVE apagar a pasta /backend/vector_db para que o sistema reindexe os documentos.
- O backend roda por padrao na porta 8000 e o frontend na porta 5173. Certifique-se de que essas portas estao livres.
