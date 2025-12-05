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
        r"(MINUTA )?RESOLUÇÃO (?:CONDEL(?:/SUDECO|/SUDENE|/SUDAM)?) Nᵒ "
        r"(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+(\w+|xx|XX)\s+DE\s+(\d{4})",
        re.IGNORECASE
    )
    
    match = padrao.search(texto_completo)
    
    if not match:
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (bolinha especial)."]}
        return {"status": "FALHA", "detalhe": ["Padrão 'RESOLUÇÃO CONDEL... Nᵒ ...' não encontrado."]}

    return {"status": "OK", "detalhe": "Epígrafe correta."}

def auditar_preambulo_condel(texto_completo):
    
    erros = []
    
    autoridades_map = {
        "SUDECO": "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "SUDAM": "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "SUDENE": "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE",
    }

    # 1. Verifica se alguma das autoridades corretas está presente (exatamente igual)
    autoridade_correta_encontrada = False
    for auth_texto in autoridades_map.values():
        if auth_texto in texto_completo:
            autoridade_correta_encontrada = True
            break
            
    if not autoridade_correta_encontrada:
        # 2. Tenta descobrir qual o usuário QUERIA usar
        sugestao_focada = None
        sigla_detectada = ""
        
        for sigla, auth_texto in autoridades_map.items():
            if sigla in texto_completo.upper():
                sugestao_focada = auth_texto
                sigla_detectada = sigla
                break
        
        if sugestao_focada:
            erros.append(f"Autoridade incorreta detectada para <strong>{sigla_detectada}</strong>.<br><br>O texto correto deve ser exato:<br><em>'{sugestao_focada}'</em>")
        else:
            lista_opcoes = "<br><br>".join([f"• {txt}" for txt in autoridades_map.values()])
            erros.append(f"Autoridade não identificada. Utilize uma das opções padrão:<br><div style='font-size:0.85em; margin-top:5px'>{lista_opcoes}</div>")
    
    # Verifica o fecho
    if "resolveu:" not in texto_completo:
        erros.append("Fecho incorreto. Esperado: 'resolveu:'.")

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo correto."}