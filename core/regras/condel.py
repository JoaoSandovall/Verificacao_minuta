import re 
from core.regras.comuns import verificar_fecho_preambulo

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
    
    autoridades_map = {
        "SUDECO": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "SUDAM": "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "SUDENE": "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE",
        "COARIDE": "O PRESIDENTE DO CONSELHO ADMINISTRATIVO DA REGIÃO INTEGRADA DE DESENVOLVIMENTO DO DISTRITO FEDERAL E ENTORNO — COARIDE"
    }
    
    sigla_encontrada = None
    
    for sigla in autoridades_map.keys():
        if sigla in texto_completo.upper():
            sigla_encontrada = sigla
            break
        
    match_linha_autoridade = re.search(r"(O PRESIDENTE DO CONSELHO.*?)(?:,|$|\n)", texto_completo, re.IGNORECASE)

    if match_linha_autoridade:
        texto_encontrado = match_linha_autoridade.group(1).strip()
        
        if sigla_encontrada:
            texto_esperado = autoridades_map[sigla_encontrada]
            
            # Normaliza para comparação
            if " ".join(texto_encontrado.split()) != " ".join(texto_esperado.split()):
                erros.append({
                    "mensagem": f"Autoridade incorreta para {sigla_encontrada}.<br>Esperado: <em>'{texto_esperado}'</em>",
                    "original": texto_encontrado, 
                    "tipo": "highlight"
                })
        else:
            erros.append({
                "mensagem": "Autoridade identificada mas sigla (SUDECO/SUDAM/ETC) não reconhecida no contexto.",
                "original": texto_encontrado,
                "tipo": "highlight"
            })
    else:
        erros.append("Linha de autoridade ('O PRESIDENTE DO CONSELHO...') não encontrada no preâmbulo.")
     
    # 2. Verifica Fecho usando a função comum (CONEXÃO AQUI)
    erros_fecho = verificar_fecho_preambulo(texto_completo)
    erros.extend(erros_fecho)

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo correto."}