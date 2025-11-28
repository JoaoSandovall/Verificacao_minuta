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
        r"(MINUTA )?RESOLUÇÃO CONDEL(?:/SUDECO|/SUDENE|/SUDAM)? Nᵒ "
        r"(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+(\w+|xx|XX)\s+DE\s+(\d{4})"
    )
    
    match = padrao.search(texto_completo)
    
    if not match:
        
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (bolinha especial)."]}
        return {"status": "FALHA", "detalhe": ["Padrão 'RESOLUÇÃO CONDEL... Nᵒ ...' não encontrado."]}

    return {"status": "OK", "detalhe": "Epígrafe CONDEL correta."}

def auditar_preambulo_condel(texto_completo):
    erros = []
    if "O PRESIDENTE DO CONSELHO DELIBERATIVO" not in texto_completo:
         erros.append("Autoridade incorreta. Esperado: 'O PRESIDENTE DO CONSELHO DELIBERATIVO...'.")
    
    if "resolveu:" not in texto_completo:
        erros.append("Fecho incorreto. Esperado: 'resolveu:'.")

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo CONDEL correto."}