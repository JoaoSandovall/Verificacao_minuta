from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.auditor import processar_minuta
import uvicorn
import io
import docx
import PyPDF2

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

@app.post("/auditar/arquivo")
async def auditar_minuta_arquivo(arquivo: UploadFile = File(...)):
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    
    extensao = arquivo.filename.split('.')[-1].lower()
    conteudo_bytes = await arquivo.read()
    texto_extraido = ""

    try:
        if extensao == 'docx':
            doc = docx.Document(io.BytesIO(conteudo_bytes))
            texto_extraido = "\n".join([paragrafo.text for paragrafo in doc.paragraphs])
        
        elif extensao == 'pdf':
            leitor_pdf = PyPDF2.PdfReader(io.BytesIO(conteudo_bytes))
            for pagina in leitor_pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Envie .docx ou .pdf")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

    if not texto_extraido.strip():
        raise HTTPException(status_code=400, detail="Não foi possível extrair texto do arquivo (pode ser um PDF escaneado como imagem).")

    resultado = processar_minuta(texto_extraido)
    
    resultado["texto_extraido"] = texto_extraido 
    return resultado

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)