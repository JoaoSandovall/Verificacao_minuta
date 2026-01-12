import re
from core.utils import _roman_to_int

def auditar_formatacao_artigos(texto_completo):
    """
    Valida formatação de Artigos (Art. 1º / Art. 10.).
    Usa Regex expandido para capturar pontuação incorreta no próprio match.
    """
    erros = []
    
    padrao = re.compile(r'^(\s*)Art\.\s*(\d+)([\. \tº°ᵒ]*)', re.MULTILINE)
    
    matches = list(padrao.finditer(texto_completo))
    
    for match in matches:
        indentacao = match.group(1) 
        numero = int(match.group(2))
        sujeira = match.group(3)
        texto_capturado = match.group(0)
        msgs_erro = []
        correcao = None
        
        # Caso 1: Artigos Ordinais (1 ao 9) -> Esperado: "Art. Xº  "
        if 1 <= numero <= 9:
            # Verifica se tem o símbolo 'ᵒ' (ordinal correto)
            if 'º' not in sujeira:
                if any(x in sujeira for x in ['ᵒ', '°']): msgs_erro.append("símbolo incorreto (use 'º')")
                elif '.' in sujeira: msgs_erro.append("uso de ponto final (use 'º')")
                else: msgs_erro.append("ausência de indicador ordinal")
            
            # Verifica espaçamento (deve terminar com 2 espaços)
            if not sujeira.endswith('  '): 
                msgs_erro.append("espaçamento incorreto (esperado 2 espaços após o símbolo)")
                
            if msgs_erro:
                correcao = f"{indentacao}Art. {numero}º  "

        # Caso 2: Artigos Cardinais (10 em diante) -> Esperado: "Art. X.  "
        elif numero >= 10:
            if '.' not in sujeira:
                if any(x in sujeira for x in ['º', '°', 'ᵒ']): msgs_erro.append("uso de ordinal (use ponto final)")
                else: msgs_erro.append("ausência de ponto final")
            
            if not sujeira.endswith('  '):
                msgs_erro.append("espaçamento incorreto (esperado 2 espaços após o ponto)")
                
            if msgs_erro:
                correcao = f"{indentacao}Art. {numero}.  "
        
        if msgs_erro:
            texto_msg = " e ".join(msgs_erro)
            texto_msg = texto_msg[0].upper() + texto_msg[1:]
            
            erros.append({
                "mensagem": f"No 'Art. {numero}': {texto_msg}.",
                "original": texto_capturado,
                "sugestao": correcao,
                "span": match.span(),
                "tipo": "fixable"
            })
    
    if not erros: return {"status": "OK", "detalhe": "Artigos corretos."}
    return {"status": "FALHA", "detalhe": erros}


def auditar_formatacao_paragrafo(texto_completo):
    """
    Valida Parágrafos (§ 1º, § 10., Parágrafo único.).
    """
    erros = []
    
    # --- PARÁGRAFOS NUMERADOS (§) ---
    # Grupo 1: Indentação
    # "§" literal
    # Espaços
    # Grupo 2: Número
    # Grupo 3: Sujeira (pontos, graus, espaços)
    padrao_num = re.compile(r'^(\s*)§\s+(\d+)([\. \tº°ᵒ]*)', re.MULTILINE)
    
    for match in padrao_num.finditer(texto_completo):
        indentacao = match.group(1)
        numero = int(match.group(2))
        sujeira = match.group(3)
        
        texto_capturado = match.group(0)
        
        msgs_erro = []
        correcao = None

        if 1 <= numero <= 9:
            if 'º' not in sujeira:
                if any(x in sujeira for x in ['ᵒ', '°']): msgs_erro.append("símbolo incorreto (use 'º')")
                elif '.' in sujeira: msgs_erro.append("uso de ponto final (use 'º')")
                else: msgs_erro.append("símbolo ausente")
            
            if not sujeira.endswith('  '):
                msgs_erro.append("espaçamento incorreto (esperado 2 espaços)")
                
            if msgs_erro: 
                correcao = f"{indentacao}§ {numero}º  "

        elif numero >= 10:
            if '.' not in sujeira:
                if any(x in sujeira for x in ['º', '°', 'ᵒ']): msgs_erro.append("uso de ordinal (use ponto final)")
                else: msgs_erro.append("ausência de ponto final")
            
            if not sujeira.endswith('  '):
                msgs_erro.append("espaçamento incorreto (esperado 2 espaços)")
            
            if msgs_erro: 
                correcao = f"{indentacao}§ {numero}.  "

        if msgs_erro:
            texto_msg = " e ".join(msgs_erro)
            texto_msg = texto_msg[0].upper() + texto_msg[1:]
            erros.append({
                "mensagem": f"No '§ {numero}': {texto_msg}.",
                "original": texto_capturado,
                "sugestao": correcao,
                "span": match.span(), 
                "tipo": "fixable"
            })

    # --- PARÁGRAFO ÚNICO ---
    # Captura a indentação (G1) e os espaços depois do ponto (G2)
    padrao_unico = re.compile(r'^(\s*)Parágrafo\s+único\.([ \t]*)', re.MULTILINE | re.IGNORECASE)
    
    for match in padrao_unico.finditer(texto_completo):
        indentacao = match.group(1)
        espacos_pos = match.group(2)
        texto_capturado = match.group(0)
        
        # A regra diz que deve haver exatamente dois espaços após o ponto
        if espacos_pos != "  ":
            erros.append({
                "mensagem": "Após 'Parágrafo único.', deve haver dois espaços.",
                "original": texto_capturado,
                "sugestao": f"{indentacao}Parágrafo único.  ",
                "span": match.span(),
                "tipo": "fixable"
            })

    if not erros: return {"status": "OK", "detalhe": "Parágrafos corretos."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_data(texto_completo):
    erros = []
    regex_data = re.compile(r"\b0[1-9]\s+de\s+(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", re.IGNORECASE)
    
    for match in regex_data.finditer(texto_completo):
        texto_errado = match.group(0)
        erros.append({
            "mensagem": "Não se deve usar zero à esquerda em datas por extenso.",
            "original": texto_errado,
            "span": match.span(),
            "tipo": "highlight"
        })

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Datas corretas."}

def auditar_uso_siglas(texto_completo):
    """
    Verifica o uso de siglas.
    Regra: Siglas devem ser introduzidas por travessão (—), evitando parênteses ou hífens.
    """
    erros = []
    
    # --- CASO 1: Sigla entre Parênteses ---
    regex_parenteses = re.compile(r"(\()([A-Z]{3,})(\))") 
    
    for match in regex_parenteses.finditer(texto_completo):
        sigla = match.group(2) 
        
        if re.fullmatch(r"[IVXLCDM]+", sigla): 
            continue

        erros.append({
            "mensagem": f"Definição de sigla ({sigla}): use travessão (— {sigla}) em vez de parênteses.",
            "original": match.group(0),
            "span": match.span(),
            "tipo": "highlight"
        })

    # --- CASO 2: Sigla com Hífen Comum ---
    regex_hifen = re.compile(r"(\s+-\s*)([A-Z]{3,})\b")
    
    for match in regex_hifen.finditer(texto_completo):
        sigla = match.group(2)            
        
        if re.fullmatch(r"[IVXLCDM]+", sigla): 
            continue

        erros.append({
            "mensagem": f"Separação de sigla ({sigla}): use travessão (—) em vez de hífen (-).",
            "original": match.group(0),
            "span": match.span(),
            "tipo": "highlight"
        })

    if erros:
        return {"status": "FALHA", "detalhe": erros}
    
    return {"status": "OK", "detalhe": "Uso de siglas correto."}

def auditar_pontuacao_incisos(texto_completo):
    """
    Verifica APENAS a pontuação final (; ou .).
    Substitui a antiga auditar_formatacao_incisos.
    """
    erros = []
    padrao = re.compile(r'(^[ \t]*[IVXLCDM]+\s*[\-–—].*?)(?=\n\s*(?:[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)|$)', re.MULTILINE | re.DOTALL)
    
    matches = list(padrao.finditer(texto_completo))
    
    if not matches: return {"status": "OK", "detalhe": "Nenhum inciso."}
    
    for match in matches:
        raw_text = match.group(1)
        texto = raw_text.strip()
        numeral = re.match(r'^\s*([IVXLCDM]+)', texto).group(1)
        
        # Cálculo de Span Justo
        offset_inicio = raw_text.find(texto)
        if offset_inicio == -1: offset_inicio = 0
        start_index = match.start(1) + offset_inicio
        span_justo = (start_index, start_index + len(texto))
        
        # Analisa o contexto (o que vem depois)
        pos_fim = match.end()
        prox = texto_completo[pos_fim:pos_fim+200].lstrip()
        is_last = True
        
        if re.match(r'[IVXLCDM]+\s*[\-–—]', prox): is_last = False
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)', prox) or not prox: is_last = True
        
        if texto.endswith(':'): continue

        if is_last:
            if not texto.endswith('.'):
                erros.append({
                    "mensagem": f"Último inciso ({numeral}) deve terminar com ponto final.",
                    "original": texto,
                    "span": span_justo,
                    "tipo": "highlight"
                })
        else:
            if not re.search(r';(\s*(e|ou))?$', texto, re.IGNORECASE):
                erros.append({
                    "mensagem": f"Inciso intermediário ({numeral}) deve terminar com ponto e vírgula (;).",
                    "original": texto,
                    "span": span_justo,
                    "tipo": "highlight"
                })

    if not erros: return {"status": "OK", "detalhe": "Pontuação correta."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_incisos(texto_completo):
    """
    Verifica APENAS a numeração romana (I, II, III...).
    """
    
    erros = []
    
    padrao = re.compile(r'(?:^|[\n\r;])\s*([IVXLCDM]+\s*[\-–—])', re.MULTILINE)
    
    matches = list(padrao.finditer(texto_completo))
    
    if not matches: return {"status": "OK", "detalhe": "Nenhum inciso."}
    
    expected = 1
    
    for i, match in enumerate(matches):
        raw_text = match.group(1) # Ex: "I -"
        texto_limpo = raw_text.strip().replace('-', '').replace('–', '').replace('—', '').strip()
        
        try:
            val = _roman_to_int(texto_limpo)
        except:
            continue

        if i > 0:
            gap = texto_completo[matches[i-1].end() : match.start()]
            
            if re.search(r'(?:^|[\n\r])\s*(?:Art\.|§|CAPÍTULO|Seção|ANEXO|Parágrafo)', gap, re.IGNORECASE):
                expected = 1

        start_index = match.start(1)
        span_justo = (start_index, start_index + len(raw_text))

        if val == expected:
            expected += 1
        else:
            is_typo = False
            if i + 1 < len(matches):
                prox_raw = matches[i+1].group(1).strip().replace('-', '').replace('–', '').replace('—', '').strip()
                
                gap_prox = texto_completo[match.end() : matches[i+1].start()]
                if not re.search(r'(?:^|[\n\r])\s*(?:Art\.|§|CAPÍTULO|Seção|ANEXO)', gap_prox, re.IGNORECASE):
                    try:
                        prox_val = _roman_to_int(prox_raw)
                        if prox_val == expected + 1:
                            is_typo = True
                    except:
                        pass

            erros.append({
                "mensagem": f"Sequência incorreta. Esperado '{expected}', achou '{val}'.",
                "original": texto_limpo,
                "span": span_justo,
                "tipo": "highlight"
            })

            if is_typo:
                expected += 1
            else:
                expected = val + 1

    if not erros: return {"status": "OK", "detalhe": "Sequência correta."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_formatacao_alineas(texto_completo):
    erros = []
    padrao = re.compile(r'(^\s*[a-z]\).*?)(?=\n\s*(?:[a-z]\)|[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO)|$)', re.MULTILINE | re.DOTALL)
    
    matches = list(padrao.finditer(texto_completo))
    
    if not matches: return {"status": "OK", "detalhe": "Nenhuma alínea."}
    
    for i, match in enumerate(matches):
        raw_text = match.group(1)
        texto = raw_text.strip()
        
        offset_inicio = raw_text.find(texto)
        if offset_inicio == -1: offset_inicio = 0
        
        start_index = match.start(1) + offset_inicio
        end_index = start_index + len(texto)
        span_justo = (start_index, end_index)

        letra = texto[0]
        trecho_contexto = texto[:60] + "..." 
        ord_letra = ord(letra)
        
        # Validação de Sequência
        if letra != 'a' and i > 0:
            prev = matches[i-1].group(1).strip()
            gap = texto_completo[matches[i-1].end():match.start()]
            if not re.search(r'(Art\.|§|[IVXLCDM])', gap) and ord_letra != ord(prev[0]) + 1:
                 erros.append({
                    "mensagem": f"Sequência alíneas incorreta. Achou '{letra})'. Trecho: '{trecho_contexto}'",
                    "original": texto,
                    "span": span_justo,
                    "tipo": "highlight"
                 })
        
        pos_fim = match.end()
        prox = texto_completo[pos_fim:pos_fim+200].lstrip()
        is_final = False
        is_middle = False
        
        if re.match(r'[a-z]\)', prox): is_middle = True
        elif re.match(r'[IVXLCDM]+\s*[\-–—]', prox): is_middle = True
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|ANEXO)', prox) or not prox: is_final = True
        else: is_final = True
        
        # Validação de Pontuação
        if is_final:
            if not texto.endswith('.'):
                erros.append({
                    "mensagem": f"Última alínea ('{letra})') sem ponto final. Trecho: '{trecho_contexto}'",
                    "original": texto,
                    "span": span_justo,
                    "tipo": "highlight"
                })
        elif is_middle:
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                 erros.append({
                    "mensagem": f"Alínea intermediária ('{letra})') deve ter ponto e vírgula. Trecho: '{trecho_contexto}'",
                    "original": texto,
                    "span": span_justo,
                    "tipo": "highlight"
                })

    if not erros: return {"status": "OK", "detalhe": "Alíneas corretas."}
    return {"status": "FALHA", "detalhe": erros[:50]}