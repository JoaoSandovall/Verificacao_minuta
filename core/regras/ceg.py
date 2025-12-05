import re

def auditar_cabecalho_ceg(texto_completo):
    """Aceita Ministério com ou sem '/Secretaria Executiva'."""
    padrao_base = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    if not primeiras_linhas:
        return {"status": "FALHA", "detalhe": ["Documento vazio."]}
    
    linha1 = primeiras_linhas[0].strip()
    
    # Aceita exato ou com sufixo
    if linha1 == padrao_base or linha1 == f"{padrao_base}/SECRETARIA EXECUTIVA" or linha1 == f"{padrao_base}/Secretaria Executiva":
        return {"status": "OK", "detalhe": "Cabeçalho CEG correto."}
    
    return {"status": "FALHA", "detalhe": [f"Cabeçalho deve ser '{padrao_base}' (opcional: /Secretaria Executiva). Encontrado: '{linha1}'"]}

def auditar_epigrafe_ceg(texto_completo):
    
    """
    Verifica epígrafe CEG.
    Aceita:
    - RESOLUÇÃO CEG/MIDR
    - MINUTA DE RESOLUÇÃO CEG/MIDR
    - MINUTA RESOLUÇÃO CEG/MIDR
    Exige: Nᵒ (bolinha especial) e datas no padrão.
    """
    
    # 1. Verifica erros comuns de formatação (hífen ou espaço na sigla)
    if re.search(r"RESOLUÇÃO\s+CEG[- ]MIDR", texto_completo, re.IGNORECASE):
        return {"status": "FALHA", "detalhe": ["A epígrafe deve usar barra '/' (CEG/MIDR). Hífen ou espaço não são permitidos."]}

    padrao = re.compile(
        r"(?:MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+CEG/MIDR\s+Nᵒ\s+(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+|xx|XX)\s+DE\s+(\d{4}|xx|XX)",
        re.IGNORECASE
    )
    
    match = padrao.search(texto_completo)
    
    if not match:
        # Se não achou, verifica se o erro foi apenas o símbolo do número
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (bolinha especial)."]}
        
        return {"status": "FALHA", "detalhe": ["Não encontrado o padrão de epígrafe CEG/MIDR correto (Verifique 'Nᵒ', datas e prefixos 'MINUTA DE...')."]}
    
    return {"status": "OK", "detalhe": "Epígrafe CEG/MIDR correta."}

def auditar_preambulo_ceg(texto_completo):
    
    erros = []
    
    # 1. Verifica Autoridade e Travessão
    match_autoridade = re.search(r"(O COORDENADOR.*?REGIONAL)\s*([-–—])\s*CEG/MIDR", texto_completo, re.DOTALL)
    
    if match_autoridade:
        separador = match_autoridade.group(2)
        if separador != '—': # Se não for o travessão grande
            erros.append(f"Separador da sigla incorreto. Deve ser um travessão (—). Encontrado: '{separador}'.")
    else:
        if "O COORDENADOR DO COMITÊ" not in texto_completo:
            erros.append("Autoridade incorreta. Esperado: 'O COORDENADOR DO COMITÊ ESTRATÉGICO...'.")
        elif "CEG/MIDR" not in texto_completo:
            erros.append("Sigla da autoridade 'CEG/MIDR' não encontrada no preâmbulo.")

    # 2. Verifica Fecho (Flexível)
    tem_fecho_minusculo = "resolve:" in texto_completo
    
    if not tem_fecho_minusculo:
        erros.append("Fecho do preâmbulo não encontrado. Aceito: 'resolve:'")

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}