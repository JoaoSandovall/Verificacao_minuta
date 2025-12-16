import re
from core.regras.comuns import verificar_fecho_preambulo

def auditar_epigrafe_ceg(texto_completo):
    if re.search(r"RESOLUÇÃO\s+CEG[- ]MIDR", texto_completo, re.IGNORECASE):
        return {"status": "FALHA", "detalhe": ["A epígrafe deve usar barra '/' (CEG/MIDR). Hífen ou espaço não são permitidos."]}

    padrao = re.compile(
        r"(?:MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+CEG/MIDR\s+Nᵒ\s+(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+|xx|XX)\s+DE\s+(\d{4}|xx|XX)",
        re.IGNORECASE
    )
    
    match = padrao.search(texto_completo)
    
    if not match:
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (bolinha especial)."]}
        
        return {"status": "FALHA", "detalhe": ["Não encontrado o padrão de epígrafe CEG/MIDR correto (Verifique 'Nᵒ', datas e prefixos 'MINUTA DE...')."]}
    
    texto_epigrafe = match.group(0)
    if not texto_epigrafe.isupper():
        return {
            "status": "FALHA",
            "detalhe": [{
                "mensagem": "A epígrafe deve estar totalmente em MAIÚSCULAS.",
                "original": texto_epigrafe,
                "tipo": "highlight"
            }]
        }
    
    return {"status": "OK", "detalhe": "Epígrafe CEG/MIDR correta."}

def auditar_preambulo_ceg(texto_completo):
    erros = []
    
    # 1. Verifica Autoridade e Travessão (Específico do CEG)
    match_autoridade = re.search(r"(O COORDENADOR.*?REGIONAL)\s*([-–—])\s*CEG/MIDR", texto_completo, re.DOTALL)
    
    if match_autoridade:
        separador = match_autoridade.group(2)
        
        if separador != '—': 
            erros.append(f"Separador da sigla incorreto. Deve ser um travessão (—). Encontrado: '{separador}'.")
    else:
        if "O COORDENADOR DO COMITÊ" not in texto_completo:
            erros.append("Autoridade incorreta. Esperado: 'O COORDENADOR DO COMITÊ ESTRATÉGICO...'.")
        elif "CEG/MIDR" not in texto_completo:
            erros.append("Sigla da autoridade 'CEG/MIDR' não encontrada no preâmbulo.")

    # 2. Verifica Fecho usando a função comum (CONEXÃO AQUI)
    erros_fecho = verificar_fecho_preambulo(texto_completo)
    erros.extend(erros_fecho)

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}