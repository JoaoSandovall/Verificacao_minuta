import re
from core.regras import resolucao
from core.utils import is_totalmente_maiusculo

def auditar_epigrafe_coaride(texto_completo):
    
    match = re.search(
        r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+(COARIDE.*?)(?=\n|$)", 
        texto_completo, 
        re.IGNORECASE
    )
    
    if match:
        texto_encontrado = match.group(0).strip()
        span = match.span()

        if "COARIDE" not in texto_encontrado.upper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Epígrafe deve conter a sigla 'COARIDE'.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
            
        if not is_totalmente_maiusculo(texto_encontrado): 
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "A epígrafe deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }

        return {"status": "OK", "detalhe": "Epígrafe COARIDE correta."}

    return {"status": "ALERTA", "detalhe": "Epígrafe COARIDE não encontrada."}

def auditar_preambulo_coaride(texto_completo):

    autoridade_esperada = "O PRESIDENTE DO CONSELHO ADMINISTRATIVO DA REGIÃO INTEGRADA DE DESENVOLVIMENTO DO DISTRITO FEDERAL E ENTORNO — COARIDE/SUDECO"

    match = re.search(
        r"(O PRESIDENTE DO CONSELHO ADMINISTRATIVO.*?)(?=\s*,|\s+no uso)", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    if match:
        
        texto_encontrado = match.group(1).strip()
        span = match.span(1)
        texto_norm = re.sub(r'\s+', ' ', texto_encontrado).upper()
        esperado_norm = re.sub(r'\s+', ' ', autoridade_esperada).upper()

        if texto_norm != esperado_norm:
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Autoridade incorreta para COARIDE.<br>Verifique a grafia e a sigla (COARIDE/SUDECO).",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
        
        if not is_totalmente_maiusculo(texto_encontrado):
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "O preâmbulo deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
            
        erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
        if erros_fecho:
            return {"status": "FALHA", "detalhe": erros_fecho}

        return {"status": "OK", "detalhe": "Preâmbulo COARIDE correto."}

    return {"status": "ALERTA", "detalhe": "Autoridade do COARIDE não encontrada no preâmbulo."}