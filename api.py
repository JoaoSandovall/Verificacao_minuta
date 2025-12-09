from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.auditor import processar_minuta

app = FastAPI(title="Auditor de Minutas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class MinutaInput(BaseModel):
    texto: str

@app.post("/auditar")
async def auditar_minuta(dados: MinutaInput):
    resultado = processar_minuta(dados.texto)
    return resultado

app.mount("/", StaticFiles(directory="static", html=True), name="static")
    