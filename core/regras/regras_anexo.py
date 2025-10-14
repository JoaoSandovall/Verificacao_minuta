# core/regras/regras_anexo.py
import re

def auditar_anexo(texto_completo):
    """Verifica se o documento contém uma seção 'ANEXO'."""
    
    match = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    
    if match:
        # Verifica se a palavra ANEXO está em maiúsculas
        if 'ANEXO' in match.group(0):
             return {"status": "OK", "detalhe": "A seção 'ANEXO' foi encontrada e está em maiúsculas."}
        else:
            return {"status": "FALHA", "detalhe": ["A palavra 'Anexo' foi encontrada, mas deve estar em maiúsculas: 'ANEXO'."]}
    else:
        # Se não há anexo, não consideramos um erro, apenas informamos.
        return {"status": "OK", "detalhe": "O documento não parece conter uma seção 'ANEXO'."}