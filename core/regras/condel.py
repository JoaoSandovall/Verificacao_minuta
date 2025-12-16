import re
from core.regras.comuns import verificar_fecho_preambulo

def _normalizar(texto):
    """Remove espaços extras, tabs e deixa tudo maiúsculo para comparação."""
    return " ".join(texto.split()).upper()

# --- FUNÇÃO DE CABEÇALHO ---
def auditar_cabecalho_condel(texto_completo):
    # Pega as primeiras linhas não vazias
    linhas = [l.strip() for l in texto_completo.strip().split('\n') if l.strip()]
    
    if len(linhas) < 3:
        return {"status": "FALHA", "detalhe": ["Cabeçalho incompleto. Esperado 3 linhas: Ministério, Superintendência e Conselho."]}

    erros = []
    
    # Linha 1: Ministério
    esperado_l1 = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    if _normalizar(linhas[0]) != _normalizar(esperado_l1):
        erros.append(f"Linha 1 incorreta.<br>Esperado: <em>{esperado_l1}</em><br>Encontrado: {linhas[0]}")

    # Linha 2: Superintendência (Aceita SUDECO, SUDAM ou SUDENE)
    aceitos_l2 = [
        "SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE",
        "SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA",
        "SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE"
    ]
    
    linha2_norm = _normalizar(linhas[1])
    encontrou_l2 = any(linha2_norm == _normalizar(aceito) for aceito in aceitos_l2)
    
    if not encontrou_l2:
        lista_formatada = "<br>".join([f"- {item}" for item in aceitos_l2])
        erros.append(f"Linha 2 incorreta.<br>Esperado uma destas:<br>{lista_formatada}<br>Encontrado: {linhas[1]}")

    # Linha 3: Conselho
    esperado_l3 = "CONSELHO DELIBERATIVO"
    if _normalizar(linhas[2]) != _normalizar(esperado_l3):
        erros.append(f"Linha 3 incorreta.<br>Esperado: <em>{esperado_l3}</em><br>Encontrado: {linhas[2]}")

    if erros:
        return {"status": "FALHA", "detalhe": erros}

    return {"status": "OK", "detalhe": "Cabeçalho CONDEL correto."}

def auditar_epigrafe_condel(texto_completo):
    
    padrao = re.compile(
        r"(MINUTA )?RESOLUÇÃO CONDEL(?:/SUDECO|/SUDENE|/SUDAM)? Nᵒ "
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
        "SUDECO": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "SUDAM": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "SUDENE": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE"
    }
    
    sigla_encontrada = None
    texto_upper = texto_completo.upper()
    
    if "DESENVOLVIMENTO DA AMAZÔNIA" in texto_upper or "SUDAM" in texto_upper:
        sigla_encontrada = "SUDAM"
    elif "DESENVOLVIMENTO DO NORDESTE" in texto_upper or "SUDENE" in texto_upper:
        sigla_encontrada = "SUDENE"
    elif "DESENVOLVIMENTO DO CENTRO-OESTE" in texto_upper or "SUDECO" in texto_upper:
        sigla_encontrada = "SUDECO"
    
    # Se ainda não achou, tenta o fallback pelas chaves do mapa
    if not sigla_encontrada:
        for sigla in autoridades_map.keys():
            if sigla in texto_upper:
                sigla_encontrada = sigla
                break

    match_linha_autoridade = re.search(r"(O PRESIDENTE DO CONSELHO.*?)(?:,|$|\n)", texto_completo, re.IGNORECASE)

    if match_linha_autoridade:
        texto_encontrado = match_linha_autoridade.group(1).strip()
        
        if sigla_encontrada:
            texto_esperado = autoridades_map[sigla_encontrada]
            
            # Compara normalizado
            if _normalizar(texto_encontrado) != _normalizar(texto_esperado):
                erros.append({
                    "mensagem": f"Autoridade incorreta para {sigla_encontrada}.<br>Esperado: <em>'{texto_esperado}'</em>",
                    "original": texto_encontrado, 
                    "tipo": "highlight"
                })
        else:
            erros.append({
                "mensagem": "Autoridade identificada mas sigla (SUDECO/SUDAM/SUDENE) não reconhecida.",
                "original": texto_encontrado,
                "tipo": "highlight"
            })
    else:
        erros.append("Linha de autoridade ('O PRESIDENTE DO CONSELHO...') não encontrada no preâmbulo.")
     
    # Verifica Fecho (chamando a função do comuns.py)
    erros_fecho = verificar_fecho_preambulo(texto_completo)
    erros.extend(erros_fecho)

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo correto."}