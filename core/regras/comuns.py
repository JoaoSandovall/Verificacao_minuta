import re
from core.utils import _roman_to_int

# --- REGRAS DE ESTRUTURA GERAL ---

def auditar_numeracao_artigos(texto_completo):
    """Verifica a numeração e o espaçamento dos artigos que INICIAM uma linha."""
    erros = []
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        pos_fim_match = match.end()
        # Pega um trecho maior para contexto
        match_texto_completo = match.string[match.start():match.end()+20].split('\n')[0]
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        if 1 <= numero_artigo <= 9:
            padrao_esperado = "°  " 
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('º'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use '°'. Trecho: '{match_texto_completo}...'")
                elif not trecho_apos_artigo.startswith('°'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal '°'. Trecho: '{match_texto_completo}...'")
                elif not trecho_apos_artigo.startswith('°  '):
                    erros.append(f"Após 'Art. {numero_artigo}°', deve haver dois espaços. Trecho: '{match_texto_completo}...'")
        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('°') or trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' deve usar ponto final (.), não ordinal. Trecho: '{match_texto_completo}...'")
                elif not trecho_apos_artigo.startswith('.'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido por ponto (.). Trecho: '{match_texto_completo}...'")
                elif not trecho_apos_artigo.startswith('.  '):
                     erros.append(f"Após 'Art. {numero_artigo}.', deve haver dois espaços. Trecho: '{match_texto_completo}...'")

    if not erros:
        return {"status": "OK", "detalhe": "A numeração e espaçamento dos artigos estão corretos."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:10]}

def auditar_espacamento_paragrafo(texto_completo):
    """Verifica parágrafos (§). Aceita '§ 10' sem ponto."""
    erros = []
    matches_numerados = re.finditer(r'^\s*§\s+(\d+)', texto_completo, re.MULTILINE)

    for match in matches_numerados:
        numero_paragrafo_str = match.group(1)
        numero_paragrafo = int(numero_paragrafo_str)
        pos_fim_match = match.end()
        trecho_apos_numero = texto_completo[pos_fim_match : pos_fim_match + 3]
        match_texto = match.group(0)

        if 1 <= numero_paragrafo <= 9:
            if not trecho_apos_numero.startswith("°  "):
                erros.append(f"O '§ {numero_paragrafo}' deve ter '°' e dois espaços. Trecho: '{match_texto}...'")

        elif numero_paragrafo >= 10:
            if trecho_apos_numero.startswith('°') or trecho_apos_numero.startswith('º'):
                 erros.append(f"O '§ {numero_paragrafo}' não deve usar ordinal. Trecho: '{match_texto}...'")
            elif trecho_apos_numero.startswith('.'):
                if not trecho_apos_numero.startswith('.  '):
                    erros.append(f"Após '§ {numero_paragrafo}.', deve haver dois espaços. Trecho: '{match_texto}...'")
            elif trecho_apos_numero.startswith(' '):
                if not trecho_apos_numero.startswith('  '):
                     erros.append(f"Após '§ {numero_paragrafo}' (sem ponto), deve haver dois espaços. Trecho: '{match_texto}...'")
            else:
                erros.append(f"Formatação inválida após '§ {numero_paragrafo}'. Trecho: '{match_texto}...'")

    matches_unicos = re.finditer(r'^\s*Parágrafo\s+único\.', texto_completo, re.MULTILINE)
    for match in matches_unicos:
        pos_fim_match = match.end()
        if not texto_completo[pos_fim_match : pos_fim_match + 2] == "  ":
            erros.append(f"Após 'Parágrafo único.', deve haver dois espaços. Trecho: '{match.group(0)}...'")

    if not erros:
        return {"status": "OK", "detalhe": "O espaçamento dos parágrafos está correto."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:10]}

def auditar_data_sem_zero_esquerda(texto_completo):
    erros = []
    padrao_data = re.compile(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+)\s+de\s+(\d{4})", re.IGNORECASE)
    meses_validos = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    for match in re.finditer(padrao_data, texto_completo):
        dia_str, mes_str, _ = match.groups()
        if mes_str.lower() not in meses_validos: continue
        if len(dia_str) == 2 and dia_str.startswith('0'):
            erros.append(f"Data com zero à esquerda: '{match.group(0)}'.")

    if not erros:
        return {"status": "OK", "detalhe": "Datas corretas."}
    return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_uso_siglas(texto_completo):
    erros = []
    for match in re.finditer(r'\([A-Z]{2,}\)', texto_completo):
        erros.append(f"Sigla em parênteses: '{match.group(0)}'. Use travessão. Trecho: '{match.group(0)}'")
    
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("Sigla 'FDCO' sem travessão. Trecho: 'Centro-Oeste FDCO'")
        
    if not erros: return {"status": "OK", "detalhe": "Siglas corretas."}
    return {"status": "FALHA", "detalhe": erros}

# --- REGRAS DE CONTEÚDO COMUM ---

def auditar_ementa(texto_completo):
    match = re.search(r".* DE \d{4}\s*\n+(.*)", texto_completo, re.MULTILINE)
    if match:
        texto_ementa = match.group(1).strip()
        verbo = texto_ementa.split()[0]
        if verbo not in ["Aprova", "Altera", "Dispõe", "Regulamenta", "Define", "Estabelece", "Autoriza", "Prorroga", "Revoga", "Atualização"]:
             return {"status": "FALHA", "detalhe": [f"Verbo da ementa incorreto: '{verbo}'. Trecho: '{texto_ementa[:30]}...'"]}
    return {"status": "OK", "detalhe": "Ementa correta."}

def auditar_assinatura(texto_completo):
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    texto = texto_completo[:match_anexo.start()] if match_anexo else texto_completo
    linhas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
    
    if linhas:
        ultimas = linhas[-3:]
        nome_encontrado = False
        for linha in ultimas:
            if linha.isupper() and len(linha) > 5 and " " in linha and not linha.startswith("Art"):
                nome_encontrado = True
                break
        
        if not nome_encontrado:
             return {"status": "FALHA", "detalhe": [f"O bloco de assinatura deve conter o NOME em maiúsculas."]}
    return {"status": "OK", "detalhe": "Assinatura correta."}

def auditar_fecho_vigencia(texto_completo):
    if "Esta Resolução entra em vigor" not in texto_completo:
         return {"status": "FALHA", "detalhe": ["Cláusula de vigência não encontrada."]}
    return {"status": "OK", "detalhe": "Vigência encontrada."}

# --- REGRAS DE PONTUAÇÃO ESTRITA (CORRIGIDAS - DECRETO 12.002) ---

def auditar_pontuacao_incisos(texto_completo):
    erros = []
    
    # Regex blindada: exige traço/travessão e para antes de estruturas
    padrao_inciso = re.compile(
        r'(^[ \t]*[IVXLCDM]+\s*[\-–].*?)(?=\n\s*(?:[IVXLCDM]+\s*[\-–]|Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)|$)', 
        re.MULTILINE | re.DOTALL
    )
    
    matches = list(padrao_inciso.finditer(texto_completo))
    
    if not matches:
        return {"status": "OK", "detalhe": "Nenhum inciso encontrado."}

    for i, match in enumerate(matches):
        inciso_texto = match.group(1).strip()
        match_numeral = re.match(r'^\s*([IVXLCDM]+)', inciso_texto)
        if not match_numeral: continue
        numeral_romano = match_numeral.group(1)
        current_val = _roman_to_int(numeral_romano)
        trecho_limpo = re.sub(r'\s+', ' ', inciso_texto)[:60] + "..."

        # 1. Sequência
        if current_val == 1:
            pass 
        elif i > 0:
            prev_match = matches[i-1]
            prev_romano = re.match(r'^\s*([IVXLCDM]+)', prev_match.group(1).strip()).group(1)
            prev_val = _roman_to_int(prev_romano)
            
            gap = texto_completo[prev_match.end():match.start()]
            tem_quebra_estrutural = re.search(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo)', gap)
            
            if not tem_quebra_estrutural and current_val != prev_val + 1:
                 erros.append(f"Sequência de incisos incorreta. Esperado {prev_val + 1}, mas encontrado '{numeral_romano}'. Trecho: '{trecho_limpo}'")

        # 2. Pontuação
        is_last_in_list = False
        
        if i == len(matches) - 1:
            is_last_in_list = True
        else:
            prox_match = matches[i+1]
            prox_texto = prox_match.group(1)
            prox_romano = re.match(r'^\s*([IVXLCDM]+)', prox_texto).group(1)
            
            if _roman_to_int(prox_romano) == 1:
                is_last_in_list = True
            
            gap = texto_completo[match.end():prox_match.start()]
            if re.search(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo)', gap):
                is_last_in_list = True

        tem_alinea_depois = re.search(r':\s*\n\s*a\)', match.group(0) + texto_completo[match.end():match.end()+20])
        
        if tem_alinea_depois or inciso_texto.endswith(':'):
            if not inciso_texto.endswith(':'):
                erros.append(f"O Inciso {numeral_romano} precede alíneas e deve terminar com dois-pontos (:). Trecho: '{trecho_limpo}'")
            continue 

        if is_last_in_list:
            if not inciso_texto.endswith('.'):
                erros.append(f"O último inciso da lista ({numeral_romano}) deve terminar com ponto final (.). Trecho: '{trecho_limpo}'")
        else:
            if not (inciso_texto.endswith(';') or inciso_texto.endswith('; e') or inciso_texto.endswith('; ou')):
                erros.append(f"O inciso intermediário ({numeral_romano}) deve terminar com ponto e vírgula (;). Trecho: '{trecho_limpo}'")

    if not erros:
        return {"status": "OK", "detalhe": "Pontuação dos incisos correta."}
    return {"status": "FALHA", "detalhe": erros[:10]}

def auditar_pontuacao_alineas(texto_completo):
    """
    (REGRA ESTRITA) Verifica Alíneas (a, b, c...).
    ATUALIZADO: Se alínea precede INCISO, deve terminar com PONTO E VÍRGULA (;), não ponto final.
    """
    erros = []
    
    padrao_alinea = re.compile(
        r'(^\s*[a-z]\).*?)(?=\n\s*(?:[a-z]\)|[IVXLCDM]+\s*[\-–]|Art\.|§|CAPÍTULO)|$)', 
        re.MULTILINE | re.DOTALL
    )
    matches = list(padrao_alinea.finditer(texto_completo))
    
    if not matches:
        return {"status": "OK", "detalhe": "Nenhuma alínea encontrada."}

    for i, match in enumerate(matches):
        texto = match.group(1).strip()
        letra = texto[0]
        trecho_visual = re.sub(r'\s+', ' ', texto)[:60] + "..."
        current_ord = ord(letra)
        
        # 1. Sequência (reseta se achar 'a')
        if letra == 'a':
            pass
        elif i > 0:
            prev_texto = matches[i-1].group(1).strip()
            prev_letra = prev_texto[0]
            gap = texto_completo[matches[i-1].end():match.start()]
            tem_quebra = re.search(r'(Art\.|§|[IVXLCDM])', gap)
            if not tem_quebra and current_ord != ord(prev_letra) + 1:
                 erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(ord(prev_letra)+1)})', mas encontrado '{letra})'. Trecho: '{trecho_visual}'")

        # 2. Pontuação
        is_final_structure = False # Se fecha o Artigo/Bloco
        precedes_inciso = False    # Se apenas volta para o nível do Inciso
        
        if i == len(matches) - 1:
            # Se é a última alínea do texto todo, assume fim.
            is_final_structure = True
        else:
            # Olha o GAP até o próximo item (alínea ou outra coisa)
            gap = texto_completo[match.end():matches[i+1].start()]
            
            # Se achou Artigo, Parágrafo ou Capítulo -> É FIM.
            if re.search(r'(Art\.|§|CAPÍTULO|Seção)', gap):
                is_final_structure = True
            
            # Se achou Inciso (ex: III -) -> NÃO É FIM, É CONTINUAÇÃO DA LISTA PAI.
            # Nesse caso, a alínea (que fecha o inciso anterior) deve seguir a pontuação do inciso pai (;)
            elif re.search(r'[IVXLCDM]+\s*[\-–]', gap):
                precedes_inciso = True
                
            # Se o próximo item é 'a)', então este é o fim da lista atual de alíneas
            # Mas precisamos saber se o que vem depois desse 'a)' é fim ou inciso... 
            # Simplificação: Se reiniciou em 'a)', assumimos que o bloco anterior fechou.
            # Mas se fechou para virar inciso, é ;, se fechou para virar Art, é .
            # Como o gap check já cobre isso, ok.
            
            prox_letra = matches[i+1].group(1).strip()[0]
            if prox_letra == 'a' and not precedes_inciso and not is_final_structure:
                # Caso raro: a) ... b) [FIM] a) ... (duas listas de alíneas seguidas sem nada no meio?)
                # Assume ponto final por segurança.
                is_final_structure = True

        # Aplicação da Regra
        if is_final_structure:
            if not texto.endswith('.'):
                erros.append(f"A última alínea ('{letra})') deve terminar com ponto final (.). Trecho: '{trecho_visual}'")
        
        elif precedes_inciso:
            # Aqui estava o erro! Antes exigia ponto. Agora exige ponto e vírgula.
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                 erros.append(f"A alínea que antecede outro inciso ('{letra})') deve terminar com ponto e vírgula (;). Trecho: '{trecho_visual}'")
        
        else:
            # Intermediária normal (a -> b)
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                 erros.append(f"A alínea intermediária ('{letra})') deve terminar com ponto e vírgula (;). Trecho: '{trecho_visual}'")

    if not erros: return {"status": "OK", "detalhe": "Alíneas corretas."}
    return {"status": "FALHA", "detalhe": erros[:10]}