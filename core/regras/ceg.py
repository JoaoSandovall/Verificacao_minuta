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
    Estrito: RESOLUÇÃO CEG/MIDR (Barra obrigatória).
    Rejeita: CEG-MIDR, CEG MIDR.
    """
    # Procura erros comuns primeiro
    if re.search(r"RESOLUÇÃO\s+CEG[- ]MIDR N°", texto_completo):
        return {"status": "FALHA", "detalhe": ["A epígrafe deve usar barra '/' (CEG/MIDR). Hífen ou espaço não são permitidos."]}

    padrao = re.compile(r"RESOLUÇÃO\s+CEG/MIDR\s+Nº\s+(\d+|xx),\s+DE", re.IGNORECASE)
    if not padrao.search(texto_completo):
        return {"status": "FALHA", "detalhe": ["Não encontrado o padrão exato 'RESOLUÇÃO CEG/MIDR Nº ...'."]}
    
    return {"status": "OK", "detalhe": "Epígrafe CEG/MIDR correta."}

def auditar_preambulo_ceg(texto_completo):
    """
    1. Autoridade: COORDENADOR...
    2. Travessão obrigatório: '— CEG/MIDR'
    3. Fecho: 'o Colegiado resolveu:' OU 'RESOLVEU:'
    """
    erros = []
    
    # 1. Verifica Autoridade e Travessão
    # Regex busca: COORDENADOR ... REGIONAL (qualquer separador) CEG/MIDR
    match_autoridade = re.search(r"(O COORDENADOR.*?REGIONAL)\s*([-–—])\s*CEG/MIDR", texto_completo, re.DOTALL)
    
    if match_autoridade:
        separador = match_autoridade.group(2)
        if separador != '—': # Se não for o travessão grande
            erros.append(f"Separador da sigla incorreto. Deve ser um travessão (—). Encontrado: '{separador}'.")
    else:
        # Se não achou o padrão, verifica se pelo menos tem o Coordenador
        if "O COORDENADOR DO COMITÊ" not in texto_completo:
            erros.append("Autoridade incorreta. Esperado: 'O COORDENADOR DO COMITÊ ESTRATÉGICO...'.")
        elif "CEG/MIDR" not in texto_completo:
            erros.append("Sigla da autoridade 'CEG/MIDR' não encontrada no preâmbulo.")

    # 2. Verifica Fecho (Flexível)
    tem_fecho_minusculo = " RESOLVE:" in texto_completo
    tem_fecho_maiusculo = re.search(r"\n\s*RESOLVEU:\s*\n", texto_completo) # RESOLVEU: sozinho na linha
    
    if not (tem_fecho_minusculo or tem_fecho_maiusculo):
        erros.append("Fecho do preâmbulo não encontrado. Aceito: 'RESOLVE: '.")

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}