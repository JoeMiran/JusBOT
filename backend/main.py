from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# Importa a nova função com nome em português
from rag_engine import perguntar_ao_jusai

app = FastAPI(title="JusAI API")

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
        # Chama a função em português
        result = perguntar_ao_jusai(request.question, usar_rag=request.use_rag)
        return result
    except Exception as e:
        print(f"ERRO API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "JusAI operando"}