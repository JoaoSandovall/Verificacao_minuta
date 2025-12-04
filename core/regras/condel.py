import re 

def auditar_cabecalho_condel(texto_completo):
    padrao_correto = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    
    if not primeiras_linhas or not primeiras_linhas[0].strip():
        return {"status": "FALHA", "detalhe": ["Documento vazio."]}
    
    linha1 = primeiras_linhas[0].strip()
    if linha1 == padrao_correto:
        return {"status": "OK", "detalhe": "Nome do Ministério correto."}
    return {"status": "FALHA", "detalhe": [f"Cabeçalho incorreto. Esperado: '{padrao_correto}'."]}

def auditar_epigrafe_condel(texto_completo):

    padrao = re.compile(
        r"(MINUTA )?RESOLUÇÃO (?:CONDEL(?:/SUDECO|/SUDENE|/SUDAM)?|COARIDE) Nᵒ "
        r"(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+(\w+|xx|XX)\s+DE\s+(\d{4})",
        re.IGNORECASE
    )
    
    match = padrao.search(texto_completo)
    
    if not match:
        
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (bolinha especial)."]}
        
        return {"status": "FALHA", "detalhe": ["Padrão 'RESOLUÇÃO CONDEL/COARIDE... Nᵒ ...' não encontrado."]}

    return {"status": "OK", "detalhe": "Epígrafe correta."}

def auditar_preambulo_condel(texto_completo):
    erros = []
    
    autoridades_aceitas = [
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE",
        "O PRESIDENTE DO CONSELHO ADMINISTRATIVO DA REGIÃO INTEGRADA DE DESENVOLVIMENTO DO DISTRITO FEDERAL E ENTORNO — COARIDE"
    ]
    
    autoridade_encontrada = False
    for autoridade in autoridades_aceitas:
        if autoridade in texto_completo:
            autoridade_encontrada = True
            break
    if not autoridade_encontrada:
        msg = "Autoridade do preâmbulo incorreta. Deve ser uma das seguintes:\n"
        for auth in autoridades_aceitas:
            msg += f"- {auth} -"
        erros.append(msg)
    
    if "resolveu:" not in texto_completo:
        erros.append("Fecho incorreto. Esperado: 'resolveu:'.")

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CONDEL correto."}