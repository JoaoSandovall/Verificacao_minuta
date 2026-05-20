import io
import docx
import pdfplumber
from fastapi import HTTPException

def extrair_texto_docx(conteudo_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(conteudo_bytes))
    return "\n".join([paragrafo.text for paragrafo in doc.paragraphs])

def extrair_texto_pdf(conteudo_bytes: bytes) -> str:
    texto_extraido = ""
    with pdfplumber.open(io.BytesIO(conteudo_bytes)) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_extraido += texto_pagina + "\n"
    return texto_extraido

def processar_arquivo_bytes(conteudo_bytes: bytes, extensao: str) -> str:
    if extensao == 'docx':
        return extrair_texto_docx(conteudo_bytes)
    elif extensao == 'pdf':
        return extrair_texto_pdf(conteudo_bytes)
    else:
        raise HTTPException(status_code=400, detail="Formato não suportado. Envie .docx ou .pdf")