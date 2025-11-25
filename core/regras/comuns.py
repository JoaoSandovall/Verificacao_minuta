import re

def auditar_cabecalho_ministerio(texto_completo):
    """Verifica se o nome do ministério está no formato correto no início do documento."""
    padrao_correto = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    if not primeiras_linhas or not primeiras_linhas[0].strip():
        return {"status": "FALHA", "detalhe": ["O documento parece estar vazio ou sem conteúdo."]}
    
    primeira_linha_conteudo = primeiras_linhas[0].strip()
    if primeira_linha_conteudo == padrao_correto:
        return {"status": "OK", "detalhe": "O nome do Ministério está formatado corretamente."}
    else:
        detalhe_erro = f"O nome do Ministério deve ser '{padrao_correto}'. Foi encontrado: '{primeira_linha_conteudo}'."
        return {"status": "FALHA", "detalhe": [detalhe_erro]}

def auditar_numeracao_artigos(texto_completo):
    """
    Verifica a numeração e o espaçamento dos artigos que INICIAM uma linha.
    """
    erros = []
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        
        pos_fim_match = match.end()
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        if 1 <= numero_artigo <= 9:
            padrao_esperado = "°  " 
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('º'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use '°' (símbolo de grau) em vez de 'º' (ordinal).")
                elif not trecho_apos_artigo.startswith('°'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal '°'.")
                elif not trecho_apos_artigo.startswith('°  '):
                    erros.append(f"Após 'Art. {numero_artigo}°', deve haver exatamente dois espaços.")
                else:
                     erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: '°' seguido de dois espaços.")

        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('°') or trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' não deve usar o ordinal '°' ou 'º', mas sim um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido por um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.  '):
                     erros.append(f"Após 'Art. {numero_artigo}.', deve haver exatamente dois espaços.")
                else:
                    erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: '.' seguido de dois espaços.")

    if not erros:
        return {"status": "OK", "detalhe": "A numeração e espaçamento dos artigos (no início de linha) estão corretos."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}

def auditar_espacamento_paragrafo(texto_completo):
    """
    Verifica a numeração e o espaçamento dos parágrafos.
    Atualizado para aceitar '§ 10' sem ponto.
    """
    erros = []
    
    matches_numerados = re.finditer(r'^\s*§\s+(\d+)', texto_completo, re.MULTILINE)

    for match in matches_numerados:
        numero_paragrafo_str = match.group(1)
        numero_paragrafo = int(numero_paragrafo_str)
        
        pos_fim_match = match.end()
        trecho_apos_numero = texto_completo[pos_fim_match : pos_fim_match + 3]

        if 1 <= numero_paragrafo <= 9:
            padrao_esperado = "°  "
            if not trecho_apos_numero.startswith(padrao_esperado):
                if trecho_apos_numero.startswith('º'):
                    erros.append(f"No '§ {numero_paragrafo}', o símbolo ordinal está incorreto. Use '°' (símbolo de grau) em vez de 'º' (ordinal).")
                elif not trecho_apos_numero.startswith('°'):
                    erros.append(f"O '§ {numero_paragrafo}' deve ser seguido pelo ordinal '°'.")
                elif not trecho_apos_numero.startswith('°  '):
                    erros.append(f"Após '§ {numero_paragrafo}°', deve haver exatamente dois espaços.")
                else:
                    erros.append(f"A formatação após '§ {numero_paragrafo}' está incorreta. Esperado: '°' seguido de dois espaços.")

        elif numero_paragrafo >= 10:
            if trecho_apos_numero.startswith('°') or trecho_apos_numero.startswith('º'):
                 erros.append(f"O '§ {numero_paragrafo}' não deve usar o ordinal '°' ou 'º', pois é maior que 9.")
            elif trecho_apos_numero.startswith('.'):
                if not trecho_apos_numero.startswith('.  '):
                    erros.append(f"Após '§ {numero_paragrafo}.' (com ponto), deve haver exatamente dois espaços.")
            elif trecho_apos_numero.startswith(' '):
                if not trecho_apos_numero.startswith('  '):
                     erros.append(f"Após '§ {numero_paragrafo}' (sem ponto), deve haver exatamente dois espaços.")
            else:
                erros.append(f"A formatação após '§ {numero_paragrafo}' está incorreta. Esperado: '.' ou espaço, seguido de dois espaços.")

    matches_unicos = re.finditer(r'^\s*Parágrafo\s+único\.', texto_completo, re.MULTILINE)
    for match in matches_unicos:
        pos_fim_match = match.end()
        trecho_apos_paragrafo = texto_completo[pos_fim_match : pos_fim_match + 2] 
        padrao_esperado = "  " 
        if not trecho_apos_paragrafo.startswith(padrao_esperado):
            erros.append("Após 'Parágrafo único.', deve haver exatamente dois espaços.")

    if not erros:
        return {"status": "OK", "detalhe": "O espaçamento dos parágrafos (no início de linha) está correto."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}

def auditar_data_sem_zero_esquerda(texto_completo):
    """Verifica datas com zero à esquerda (ex: 09 de...)."""
    erros = []
    padrao_data = re.compile(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+)\s+de\s+(\d{4})", re.IGNORECASE)
    meses_validos = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    for match in re.finditer(padrao_data, texto_completo):
        dia_str, mes_str, ano_str = match.groups()
        if mes_str.lower() not in meses_validos:
            continue
        if len(dia_str) == 2 and dia_str.startswith('0'):
            dia_correto = str(int(dia_str)) 
            sugestao = f"'{dia_correto} de {mes_str} de {ano_str}'"
            erros.append(f"Data com dia formatado incorretamente (zero à esquerda): '{match.group(0)}'. O correto seria: {sugestao}.")

    if not erros:
        return {"status": "OK", "detalhe": "Nenhuma data com formatação de dia incorreta (zero à esquerda) foi encontrada."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_uso_siglas(texto_completo):
    """Verifica formatação de siglas."""
    erros = []
    padrao_parenteses = r'\([A-Z]{2,}\)'
    for match in re.finditer(padrao_parenteses, texto_completo):
        erros.append(f"A sigla '{match.group(0)}' não deve estar entre parênteses. Use um travessão (–).")
    
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("A sigla 'FDCO' não está separada por travessão. O correto seria '...Centro-Oeste – FDCO'.")
        
    if not erros:
        return {"status": "OK", "detalhe": "A formatação das siglas está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}