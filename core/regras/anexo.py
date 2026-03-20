import re
from core.utils import _roman_to_int

def auditar_anexo(texto_completo):
    match_correto = re.search(r'\n\s*(ANEXO)\s*(?=\n|$)', texto_completo)
    
    if match_correto:
         return {"status": "OK", "detalhe": "Seção 'ANEXO' encontrada e formatada corretamente."}
     
    match_incorreto = re.search(r'\n\s*(ANEXO\b.*?)\s*(?=\n|$)', texto_completo, re.IGNORECASE)
    
    if match_incorreto:
        palavra_encontrada = match_incorreto.group(1).strip()
        return {
                "status": "FALHA",
                "detalhe": [f"Separador de Anexo incorreto. Encontrado: '{palavra_encontrada}'. O sistema exige a palavra 'ANEXO' (exatamente assim: tudo maiúsculo e sozinha na linha) para separar a resolução do conteúdo do anexo."]
        }
        
    return {
        "status": "ALERTA",
        "detalhe": [f"O termo 'ANEXO' não foi encontrado no final do documento. Se esta resolução possui anexo, insira o título 'ANEXO' para a avaliação correta. Se essa resolução não possui anexo, ignore este aviso."]
    }
    
def auditar_sequencia_capitulos_anexo(texto_completo):
    
    erros = []
    
    matches = list(re.finditer(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE))
    
    if not matches:
        return {"status": "OK", "detalhe": "Nenhum Capítulo encontrado para análise."}
    
    expected_numeral = 1
    
    for match in matches:
        numeral_romano = match.group(1)
        texto_capitulo = match.group(0)
        current_numeral = _roman_to_int(numeral_romano)
        
        if current_numeral != expected_numeral:
            erros.append({
                "mensagem": f"Sequência de Capítulos incorreta. Esperado {expected_numeral}, encontrado '{numeral_romano}'.",
                "original": texto_capitulo, 
                "span": match.span(),
                "tipo": "highlight"        
            })
            expected_numeral = current_numeral
        expected_numeral += 1
        
    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Capítulos está correta."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_secoes_anexo(texto_completo):
    
    erros = []
    
    blocos_capitulo = re.split(r'^\s*CAPÍTULO\s+[IVXLCDM]+', texto_completo, flags=re.MULTILINE)
    capitulos_encontrados = re.findall(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    
    for i, bloco_texto in enumerate(blocos_capitulo[1:]):
        nome_capitulo = capitulos_encontrados[i] if i < len(capitulos_encontrados) else 'desconhecido'
        matches = re.finditer(r'^\s*Seção\s+([IVXLCDM]+)', bloco_texto, re.MULTILINE)
        
        expected_numeral = 1
        
        for match in matches:
            numeral_romano = match.group(1)
            current_numeral = _roman_to_int(numeral_romano)
            
            if current_numeral != expected_numeral:
                erros.append({
                    "mensagem": f"Sequência incorreta no CAPÍTULO {nome_capitulo}. Esperado Seção {expected_numeral}, mas encontrado '{numeral_romano}'.",
                    "original": match.group(0).strip(),
                    "tipo": "highlight"
                })    
                expected_numeral = current_numeral
            expected_numeral += 1
            
    if not erros: return {"status": "OK", "detalhe": "Sequência das Seções correta."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_artigos_anexo(texto_completo):
    erros = []
    
    matches = list(re.finditer(r'Art\.\s*(\d+)', texto_completo))
    
    if not matches: 
        return {"status": "OK", "detalhe": "Nenhum Artigo encontrado no Anexo para análise de sequência."}
    
    expected_num = 1
    primeiro_match = matches[0]
    primeiro_numero = int(primeiro_match.group(1))
    
    if primeiro_numero != 1:    
        erros.append({
            "mensagem": f"O primeiro Artigo do Anexo não é 'Art. 1ᵒ'. Encontrado: 'Art. {primeiro_numero}'.",
            "original": primeiro_match.group(0),
            "span": primeiro_match.span(),
            "tipo": "highlight"
        })
        expected_num = primeiro_numero
    
    for i in range(len(matches)):
        match = matches[i]
        num = int(match.group(1))
        texto_artigo = match.group(0)
        
        if num != expected_num:
            proximo_match = matches[i+1] if i + 1 < len(matches) else None
            
            eh_erro_isolado = True
            
            if proximo_match:
                prox_num_real = int(proximo_match.group(1))
                
                if prox_num_real == num + 1:
                    eh_erro_isolado = False

            if eh_erro_isolado:
                erros.append({
                    "mensagem": f"Numeração fora de sequência. Esperado 'Art. {expected_num}', mas encontrado 'Art. {num}'.",
                    "original": texto_artigo,
                    "span": match.span(),
                    "tipo": "highlight"
                })
            
            else:
                erros.append({
                    "mensagem": f"Salto na numeração detectado. Esperado 'Art. {expected_num}', mas encontrado 'Art. {num}'.",
                    "original": texto_artigo,
                    "span": match.span(),
                    "tipo": "highlight"
                })
                expected_num = num

        expected_num += 1

    if not erros: 
        return {"status": "OK", "detalhe": "A sequência dos Artigos no Anexo está correta."}
        
    return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_paragrafos_anexo(texto_completo):
    
    erros = []
    
    regex_combinado = r'(?P<artigo>^\s*Art\.\s*\d+)|(?P<paragrafo>^\s*§\s*(?P<num>\d+))'
    
    matches = list(re.finditer(regex_combinado, texto_completo, re.MULTILINE | re.IGNORECASE))
    
    if not matches:
         return {"status": "OK", "detalhe": "Nenhum parágrafo numerado (§) encontrado para análise."}

    expected_num = 1
    
    for i in range(len(matches)):
        match = matches[i]
        
        if match.group('artigo'):
            expected_num = 1
            continue
            
        if match.group('paragrafo'):
            num = int(match.group('num'))
            texto_par = match.group('paragrafo').strip()
            
            if num != expected_num:
                
                proximo_match_par = None
                
                for j in range(i + 1, len(matches)):
                    m_futuro = matches[j]
                    if m_futuro.group('artigo'): 
                        break
                    if m_futuro.group('paragrafo'):
                        proximo_match_par = m_futuro
                        break
                
                eh_erro_isolado = True
                
                if proximo_match_par:
                    prox_num_real = int(proximo_match_par.group('num'))
                    if prox_num_real == num + 1:
                        eh_erro_isolado = False
                
                if eh_erro_isolado:
                     erros.append({
                        "mensagem": f"Numeração de parágrafo fora de sequência. Esperado '§ {expected_num}', mas encontrado '§ {num}'.",
                        "original": texto_par,
                        "span": match.span(),
                        "tipo": "highlight"
                    })
                     
                else:
                    erros.append({
                        "mensagem": f"Salto na numeração de parágrafos. Esperado '§ {expected_num}', mas encontrado '§ {num}'.",
                        "original": texto_par,
                        "span": match.span(),
                        "tipo": "highlight"
                    })
                    expected_num = num
            
            expected_num += 1

    if not erros:
        return {"status": "OK", "detalhe": "Sequência de parágrafos correta."}
        
    return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_hierarquica_anexo(texto_completo):
    
    erros = []
    
    padrao_itens = re.compile(r"^(?:[ \t]*)((Art\.\s*\d+[ᵒ\.]?|Parágrafo\s+único\.?|§\s*\d+[ᵒ\.]?)|([IVXLCDM]+[\s\-–—])|([a-z]\)))(.*)", re.MULTILINE | re.IGNORECASE)
    matches = list(re.finditer(padrao_itens, texto_completo))
    
    for i, match in enumerate(matches):
        linha_completa = match.group(0).strip()
        marcador_item = match.group(1).strip()
        
        if re.match(r'^CAPÍTULO', linha_completa, re.I) or re.match(r'^Seção', linha_completa, re.I): continue
            
        tipo_atual = None
        if re.match(r'Art\.|Parágrafo|§', marcador_item, re.I): tipo_atual = "Artigo/Paragrafo"
        elif re.match(r'^[IVXLCDM]+', marcador_item): tipo_atual = "Inciso"
        elif re.match(r'^[a-z]\)', marcador_item): tipo_atual = "Alinea"

        proximo_match = matches[i + 1] if (i + 1) < len(matches) else None
        inicia_subdivisao = False
        
        if proximo_match:
            m_prox = proximo_match.group(1).strip()
            proximo_eh_inciso = bool(re.match(r'^[IVXLCDM]+', m_prox))
            proximo_eh_alinea = bool(re.match(r'^[a-z]\)', m_prox))
            if tipo_atual == "Artigo/Paragrafo" and proximo_eh_inciso: inicia_subdivisao = True
            elif tipo_atual == "Inciso" and proximo_eh_alinea: inicia_subdivisao = True
        
        msg_erro = None
        if inicia_subdivisao:
            if not linha_completa.endswith(':'): msg_erro = "Pontuação de Abertura Incorreta: deve terminar com ':'."
        elif tipo_atual == "Artigo/Paragrafo":
            if not (linha_completa.endswith('.') or linha_completa.endswith(':')): msg_erro = "Pontuação de Declaração Incorreta: deve terminar com '.' ou ':'."
        
        if msg_erro:
            
            erros.append({
                "mensagem": f"{msg_erro} Trecho: '{linha_completa[:40]}...'",
                "original": linha_completa,
                "tipo": "highlight"
            })

    if not erros: return {"status": "OK", "detalhe": "Pontuação hierárquica correta."}
    return {"status": "FALHA", "detalhe": erros[:50]}