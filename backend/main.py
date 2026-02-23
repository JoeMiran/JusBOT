from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
# Importa a nova função com nome em português
from rag_engine import perguntar_ao_itau_bot

app = FastAPI(title="Políticas Itaú API")
=======
from rag_engine import perguntar_ao_compliance_bot

app = FastAPI(title="CompBOT API")
>>>>>>> cbb4623cf8e47606c74d47ad9ebced543e17945c

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    use_rag: bool = True

@app.post("/ask")
def query_endpoint(request: QueryRequest):
    try:
<<<<<<< HEAD
        # Chama a função em português
        result = perguntar_ao_itau_bot(request.question, usar_rag=request.use_rag)
=======
        result = perguntar_ao_compliance_bot(request.question, usar_rag=request.use_rag)
>>>>>>> cbb4623cf8e47606c74d47ad9ebced543e17945c
        return result
    except Exception as e:
        print(f"ERRO API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
<<<<<<< HEAD
    return {"status": "Assistente Itaú operando"}
=======
    return {"status": "CompBOT operando"}
>>>>>>> cbb4623cf8e47606c74d47ad9ebced543e17945c
