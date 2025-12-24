import re
from core.regras import resolucao

def auditar_epigrafe_ceg(texto_completo):
    # Regex para localizar a linha da Epígrafe e calcular o SPAN (posição)
    # Procura por "RESOLUÇÃO CEG..." aceitando variações para poder apontar o erro
    match = re.search(r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+(CEG.*?)(\n|$)", texto_completo, re.IGNORECASE)
    
    if match:
        texto_encontrado = match.group(0).strip()
        span = match.span()

        if "CEG/MIDR" not in texto_encontrado.upper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "A epígrafe deve usar barra '/' (CEG/MIDR). Hífen ou espaço não são permitidos.",
                    "original": texto_encontrado,
                    "span": span,      
                    "tipo": "highlight"
                }
            }
        return {"status": "OK", "detalhe": "Epígrafe CEG correta."}

    return {"status": "ALERTA", "detalhe": "Epígrafe CEG não encontrada."}

def auditar_preambulo_ceg(texto_completo):
    """
    Valida o Preâmbulo do CEG.
    Regra: Deve citar a autoridade 'CEG/MIDR'.
    """

    match = re.search(
        r"(O (?:COORDENADOR|PRESIDENTE|COMITÊ).*?)(?=\s*,|\s+no uso)", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    if match:
        texto_encontrado = match.group(1).strip()
        span = match.span(1) # Pega a posição apenas do nome da autoridade

        # Validação: Exige a sigla exata
        if "CEG/MIDR" not in texto_encontrado.upper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Sigla da autoridade 'CEG/MIDR' não encontrada no preâmbulo.",
                    "original": texto_encontrado,
                    "span": span,       
                    "tipo": "highlight" 
                }
            }
        return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}

    return {"status": "ALERTA", "detalhe": "Preâmbulo CEG não encontrado (Esperado: 'O COORDENADOR...')."}