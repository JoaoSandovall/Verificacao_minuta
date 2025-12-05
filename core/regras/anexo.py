import re
from core.utils import _roman_to_int

def auditar_anexo(texto_completo):
    """Verifica se a seção 'ANEXO' existe e formatação."""
    match_correto = re.search(r'\n\s*(ANEXO)\s*(?=\n|$)', texto_completo)
    if match_correto:
         return {"status": "OK", "detalhe": "Seção 'ANEXO' encontrada e formatada corretamente."}

    match_incorreto = re.search(r'\n\s*(ANEXO\b.*?)\s*(?=\n|$)', texto_completo, re.IGNORECASE)
    if match_incorreto:
        palavra_encontrada = match_incorreto.group(1).strip()
        return {"status": "FALHA", "detalhe": [f"Formato de 'Anexo' incorreto. Encontrado: '{palavra_encontrada}'. Esperado: 'ANEXO' (exatamente, em maiúsculas e sozinho na linha)."]}
    
    return {"status": "OK", "detalhe": "Aviso: Nenhuma seção 'ANEXO' foi encontrada (Não obrigatório)."}

def auditar_sequencia_capitulos_anexo(texto_completo):
    """(Anexo) Verifica a sequência dos Capítulos (I, II, III...)."""
    erros = []
    matches = re.finditer(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    capitulos = [match.group(1) for match in matches]
    
    if not capitulos:
        return {"status": "OK", "detalhe": "Nenhum Capítulo encontrado para análise."}

    expected_numeral = 1
    for i, numeral_romano in enumerate(capitulos):
        current_numeral = _roman_to_int(numeral_romano)
        if current_numeral != expected_numeral:
            erro = f"Sequência de Capítulos incorreta. Esperado Capítulo de valor {expected_numeral} (Romano), mas encontrado '{numeral_romano}'."
            erros.append(erro)
            expected_numeral = current_numeral 
        expected_numeral += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Capítulos está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_secoes_anexo(texto_completo):
    """(Anexo) Verifica a sequência das Seções (I, II, III...) dentro de cada Capítulo."""
    erros = []
    blocos_capitulo = re.split(r'^\s*CAPÍTULO\s+[IVXLCDM]+', texto_completo, flags=re.MULTILINE)
    capitulos_encontrados = re.findall(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    
    for i, bloco_texto in enumerate(blocos_capitulo[1:]):
        nome_capitulo = capitulos_encontrados[i] if i < len(capitulos_encontrados) else 'desconhecido'
        matches = re.finditer(r'^\s*Seção\s+([IVXLCDM]+)', bloco_texto, re.MULTILINE)
        
        expected_numeral = 1
        for match in matches:
            numeral_romano = match.group(1)
            texto_encontrado = match.group(0).strip() # Ex: "Seção VII"
            
            current_numeral = _roman_to_int(numeral_romano)
            if current_numeral != expected_numeral:
                # RETORNA OBJETO PARA GRIFAR E CRIAR LINK
                erros.append({
                    "mensagem": f"Sequência incorreta no CAPÍTULO {nome_capitulo}. Esperado Seção {expected_numeral}, mas encontrado '{numeral_romano}'.",
                    "original": texto_encontrado, 
                    "tipo": "highlight"
                })
                expected_numeral = current_numeral
            expected_numeral += 1
            
    if not erros: return {"status": "OK", "detalhe": "Sequência das Seções correta."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_artigos_anexo(texto_completo):
    
    erros = []
    matches = re.finditer(r'Art\.\s*(\d+)', texto_completo)
    artigos = [int(match.group(1)) for match in matches]
    
    if not artigos:
        return {"status": "OK", "detalhe": "Nenhum Artigo encontrado no Anexo para análise de sequência."}

    expected_num = 1
    if artigos[0] != 1:
        erros.append(f"O primeiro Artigo do Anexo não é 'Art. 1ᵒ'. Encontrado: 'Art. {artigos[0]}'.")
        expected_num = artigos[0]

    for num in artigos:
        if num != expected_num:
            erros.append(f"Sequência de Artigos incorreta no Anexo. Esperado 'Art. {expected_num}', mas encontrado 'Art. {num}'.")
            expected_num = num
        expected_num += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Artigos no Anexo está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_hierarquica_anexo(texto_completo):
    erros = []
    
    padrao_itens = re.compile(
        r"^(?:[ \t]*)((Art\.\s*\d+[ᵒ\.]?|Parágrafo\s+único\.?|§\s*\d+[ᵒ\.]?)|([IVXLCDM]+[\s\-–—])|([a-z]\)))(.*)", 
        re.MULTILINE | re.IGNORECASE
    )
    
    matches = list(re.finditer(padrao_itens, texto_completo))
    
    for i, match in enumerate(matches):
        linha_completa = match.group(0).strip()
        marcador_item = match.group(1).strip()
        
        # Pula títulos de seção/capítulo
        if re.match(r'^CAPÍTULO', linha_completa, re.I) or re.match(r'^Seção', linha_completa, re.I):
            continue
            
        tipo_atual = None
        if re.match(r'Art\.|Parágrafo|§', marcador_item, re.I): tipo_atual = "Artigo/Paragrafo"
        elif re.match(r'^[IVXLCDM]+', marcador_item): tipo_atual = "Inciso"
        elif re.match(r'^[a-z]\)', marcador_item): tipo_atual = "Alinea"

        proximo_match = matches[i + 1] if (i + 1) < len(matches) else None
        
        inicia_subdivisao = False
        if proximo_match:
            marcador_proximo = proximo_match.group(1).strip()
            proximo_eh_inciso = bool(re.match(r'^[IVXLCDM]+', marcador_proximo))
            proximo_eh_alinea = bool(re.match(r'^[a-z]\)', marcador_proximo))

            if tipo_atual == "Artigo/Paragrafo" and proximo_eh_inciso: inicia_subdivisao = True
            elif tipo_atual == "Inciso" and proximo_eh_alinea: inicia_subdivisao = True
        
        # Checagens
        msg_erro = None
        
        if inicia_subdivisao:
            if not linha_completa.endswith(':'):
                msg_erro = f"Pontuação de Abertura Incorreta: deve terminar com ':'."
        elif tipo_atual == "Artigo/Paragrafo":
            if not (linha_completa.endswith('.') or linha_completa.endswith(':')):
                msg_erro = f"Pontuação de Declaração Incorreta: deve terminar com '.' ou ':'."
        elif tipo_atual in ("Inciso", "Alinea"):
            tipo_proximo = None
            if proximo_match:
                m_prox = proximo_match.group(1).strip()
                if re.match(r'Art\.|Parágrafo|§', m_prox, re.I): tipo_proximo = "Artigo/Paragrafo"
                elif re.match(r'^[IVXLCDM]+', m_prox): tipo_proximo = "Inciso"
                elif re.match(r'^[a-z]\)', m_prox): tipo_proximo = "Alinea"
            
            if (proximo_match and tipo_proximo == tipo_atual) or (tipo_atual == "Alinea" and tipo_proximo == "Inciso"):
                if not (linha_completa.endswith(';') or linha_completa.endswith('; e') or linha_completa.endswith('; ou') or linha_completa.endswith(':')):
                    msg_erro = f"Pontuação de Lista Incorreta: deve terminar com ';', '; e' ou '; ou'."
            else:
                if not (linha_completa.endswith('.') or linha_completa.endswith(':')):
                    msg_erro = f"Pontuação de Fim de Lista Incorreta: deveria terminar com '.' (ponto final)."

        if msg_erro:
            # RETORNA OBJETO PARA GRIFAR E CRIAR LINK
            # Usamos a linha completa como 'original' para grifar o parágrafo todo que está errado
            erros.append({
                "mensagem": f"{msg_erro} Trecho: '{linha_completa[:40]}...'",
                "original": linha_completa,
                "tipo": "highlight"
            })

    if not erros: return {"status": "OK", "detalhe": "Pontuação hierárquica correta."}
    return {"status": "FALHA", "detalhe": list(set([e['mensagem'] for e in erros] if not isinstance(erros[0], dict) else erros))[:10]}