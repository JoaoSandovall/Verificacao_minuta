import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.auditor import processar_minuta
from core.file_parser import processar_arquivo_bytes

import uvicorn

app = FastAPI(title="Auditor de Minutas API")

origens_permitidas = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_methods=["*"],
    allow_headers=["*"]
)

class MinutaInput(BaseModel):
    texto: str

@app.post("/auditar")
async def auditar_minuta(dados: MinutaInput):
    resultado = processar_minuta(dados.texto)
    return resultado

@app.post("/auditar/arquivo")
async def auditar_minuta_arquivo(arquivo: UploadFile = File(...)):
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    
    extensao = arquivo.filename.split('.')[-1].lower()
    conteudo_bytes = await arquivo.read()

    try:
        texto_extraido = processar_arquivo_bytes(conteudo_bytes, extensao)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

    if not texto_extraido.strip():
        raise HTTPException(status_code=400, detail="Não foi possível extrair texto do arquivo.")

    resultado = processar_minuta(texto_extraido)
    resultado["texto_extraido"] = texto_extraido 
    return resultado

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)