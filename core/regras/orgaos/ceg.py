import re
from core.regras import resolucao

def auditar_epigrafe_ceg(texto_completo):
    # Verificação extra específica do CEG (hífen vs barra)
    if re.search(r"RESOLUÇÃO\s+CEG[- ]MIDR", texto_completo, re.IGNORECASE):
        return {"status": "FALHA", "detalhe": ["A epígrafe deve usar barra '/' (CEG/MIDR). Hífen ou espaço não são permitidos."]}

    # Regex Específico do CEG
    padrao = re.compile(
        r"(?:MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+CEG/MIDR\s+Nᵒ\s+(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+|xx|XX)\s+DE\s+(\d{4}|xx|XX)",
        re.IGNORECASE
    )
    
    msg_erro = ["Não encontrado o padrão de epígrafe CEG/MIDR correto (Verifique 'Nᵒ', datas e prefixos 'MINUTA DE...')."]
    
    # Chama a função 
    return resolucao.auditar_epigrafe(texto_completo, padrao, msg_erro)

def auditar_preambulo_ceg(texto_completo):
    
    erros = []
    
    match_autoridade = re.search(r"(O COORDENADOR.*?REGIONAL)\s*([-–—])\s*CEG/MIDR", texto_completo, re.DOTALL | re.IGNORECASE)
    
    if match_autoridade:
        separador = match_autoridade.group(2)
        if separador != '—': 
            erros.append(f"Separador da sigla incorreto. Deve ser um travessão (—). Encontrado: '{separador}'.")
    else:
        if "O COORDENADOR DO COMITÊ" not in texto_completo.upper():
            erros.append("Autoridade incorreta. Esperado: 'O COORDENADOR DO COMITÊ ESTRATÉGICO...'.")
        elif "CEG/MIDR" not in texto_completo.upper():
            erros.append("Sigla da autoridade 'CEG/MIDR' não encontrada no preâmbulo.")

    erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
    erros.extend(erros_fecho)

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}