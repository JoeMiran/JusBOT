from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import perguntar_ao_itau_bot

app = FastAPI(title="Políticas Itaú API")

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

@app.get("/")
def health_check():
    return {"status": "Assistente Itaú operando"}

@app.post("/ask")
def query_endpoint(request: QueryRequest):
    try:
        # Retorna o dicionário contendo 'answer' e 'sources' definido no rag_engine.py
        return perguntar_ao_itau_bot(request.question, usar_rag=request.use_rag)
    except Exception as e:
        print(f"ERRO API: {e}")
        raise HTTPException(status_code=500, detail=str(e))