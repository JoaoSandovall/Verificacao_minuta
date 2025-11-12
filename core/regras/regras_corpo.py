import re

def _roman_to_int(s):
    """Função auxiliar para converter numerais romanos em inteiros."""
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev_value = 0
    for char in reversed(s):
        value = roman_map[char]
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    return result

def auditar_preambulo(texto_completo):
    """
    Verifica a formatação do Preâmbulo, focando na autoridade específica
    e na terminação com 'o Colegiado resolveu:'.
    """
    erros = []

    # Passo 1: Isolar o texto do preâmbulo (lógica antiga e funcional)
    try:
        match_epigrafe = re.search(r".* DE \d{4}", texto_completo, re.IGNORECASE)
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():].strip()
        
        # Remove a linha "MINUTA DE DOCUMENTO" se existir
        texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO\s*', '', texto_apos_epigrafe, flags=re.IGNORECASE).strip()

        linhas_limpas = texto_limpo.split('\n')
        texto_ementa = ""
        inicio_preambulo_texto = ""
        for i, linha in enumerate(linhas_limpas):
            if linha.strip():
                texto_ementa = linha.strip()
                # O preâmbulo começa no texto após a linha da ementa
                inicio_preambulo_texto = "\n".join(linhas_limpas[i+1:])
                break
        
        # Regex atualizada para aceitar º, o, ou °
        match_artigo1 = re.search(r'Art\.\s*1[ºo°]', inicio_preambulo_texto, re.IGNORECASE)
        
        texto_preambulo = inicio_preambulo_texto[:match_artigo1.start()].strip()

    except (AttributeError, IndexError):
        # Retorna o erro no formato de dicionário para manter a consistência
        return {"status": "FALHA", "detalhe": [{"mensagem": "Não foi possível isolar o texto do preâmbulo para análise. Verifique se a ementa e o Art. 1º existem.", "contexto": ""}]}

    if not texto_preambulo:
        return {"status": "FALHA", "detalhe": [{"mensagem": "O texto do preâmbulo parece estar vazio.", "contexto": ""}]}

    # Lógica de verificação para parágrafo único
    texto_preambulo_normalizado = re.sub(r'\s+', ' ', texto_preambulo).strip()

    # Passo 2: Verificar a Autoridade (Início)
    autoridades_validas = [
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE - CONDEL/SUDECO",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA - CONDEL/SUDAM",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE – CONDEL/SUDENE"
    ]
    
    autoridade_encontrada = False
    for autoridade in autoridades_validas:
        autoridade_normalizada = re.sub(r'\s+', ' ', autoridade)
        if texto_preambulo_normalizado.startswith(autoridade_normalizada):
            autoridade_encontrada = True
            break
            
    if not autoridade_encontrada:
        contexto_erro = texto_preambulo.split('\n')[0].strip()
        erros.append(f"O Começo do preâmbulo está incorreto. Esperado uma das autoridades válidas. Encontrado: '{contexto_erro}...'")

    # Passo 3: Verificar a Terminação (Fim)
    padrao_correto_fim = "o Colegiado resolveu:"

    if not texto_preambulo_normalizado.endswith(padrao_correto_fim):
        contexto_fim = texto_preambulo_normalizado[-50:]
        
        if texto_preambulo_normalizado.lower().endswith(padrao_correto_fim):
            erros.append(f"A terminação do preâmbulo deve ser '{padrao_correto_fim}' (exatamente, com 'o' minúsculo). Foi encontrado: '...{contexto_fim}'")
        else:
            erros.append(f"O preâmbulo deve terminar com a frase exata '{padrao_correto_fim}'. Foi encontrado: '...{contexto_fim}'")
            
    # Passo 4: Retornar o resultado
    if not erros:
        return {"status": "OK", "detalhe": "O preâmbulo está estruturado corretamente."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_numeracao_artigos(texto_completo):
    """
    (REGRA - Resolução e Anexo)
    Verifica a numeração e o espaçamento dos artigos que INICIAM uma linha.
    - Art. 1° a 9°: Deve ser 'Art. N°  ' (com ° e dois espaços).
    - Art. 10. em diante: Deve ser 'Art. NN.  ' (com . e dois espaços).
    - Artigos no meio do texto (ex: "conforme o art. 1°") são ignorados.
    """
    erros = []
    
    # Regex agora só busca artigos no INÍCIO da linha (com re.MULTILINE)
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        
        pos_fim_match = match.end()
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        # --- VALIDAÇÃO PARA ARTIGOS DE 1 A 9 ---
        if 1 <= numero_artigo <= 9:
            
            # Agora '°' (grau) é OBRIGATÓRIO
            padrao_esperado = "°  " # Símbolo de grau
    
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
                if trecho_apos_artigo.startswith('º'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use '°' (símbolo de grau) em vez de 'º' (ordinal).")
                elif not trecho_apos_artigo.startswith('°'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal '°'.")
                elif not trecho_apos_artigo.startswith('°  '):
                    erros.append(f"Após 'Art. {numero_artigo}°', deve haver exatamente dois espaços.")
                else:
                     erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: '°' seguido de dois espaços.")

        # --- VALIDAÇÃO PARA ARTIGOS 10 EM DIANTE ---
        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
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
    
def auditar_pontuacao_incisos(texto_completo):
    """(REGRA - Resolução) Verifica a sequência e a pontuação de Incisos (I, II, ...)."""
    erros = []
    # Regex para encontrar incisos (linhas que começam com numerais romanos)
    incisos = re.findall(r'(^[ \t]*[IVXLCDM]+[\s\-–].*?)(?=\n[ \t]*[IVXLCDM]+[\s\-–]|\Z)', texto_completo, re.MULTILINE | re.DOTALL)
    
    if not incisos:
        return {"status": "OK", "detalhe": "Nenhum inciso (I, II, etc.) foi encontrado para análise."}
    
    num_incisos = len(incisos)
    expected_numeral = 1

    for i, inciso_texto in enumerate(incisos):
        inciso_limpo = inciso_texto.strip()
        numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_limpo).group(1)
        
        # 1. Verificar sequência
        current_numeral = _roman_to_int(numeral_romano)
        if current_numeral != expected_numeral:
            erros.append(f"Sequência de incisos incorreta. Esperado inciso de valor {expected_numeral}, mas encontrado '{numeral_romano}'.")
        expected_numeral += 1

        # 2. Verificar pontuação
        is_last = (i == num_incisos - 1)
        is_penultimate = (i == num_incisos - 2)
        tem_alineas = re.search(r':\s*\n\s*[a-z]\)', inciso_texto)
        
        if tem_alineas:
            if not inciso_limpo.endswith(':'):
                 erros.append(f"O Inciso {numeral_romano} precede alíneas e deve terminar com dois-pontos (:).")
            continue

        if is_last:
            if not inciso_limpo.endswith('.'):
                erros.append(f"O último inciso (Inciso {numeral_romano}) deve terminar com ponto final (.). Encontrado: '{inciso_limpo[-1]}'")
        elif is_penultimate:
            if not inciso_limpo.endswith('; e'):
                erros.append(f"O penúltimo inciso (Inciso {numeral_romano}) deve terminar com '; e'.")
        else:
            if not inciso_limpo.endswith(';'):
                erros.append(f"O inciso intermediário (Inciso {numeral_romano}) deve terminar com ponto e vírgula (;).")

    if not erros:
        return {"status": "OK", "detalhe": "A sequência e pontuação dos incisos estão corretas."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]} # Limita o número de erros

def auditar_uso_siglas(texto_completo):
    """(REGRA - Resolução e Anexo) Verifica se as siglas estão usando travessão ou se estão incorretamente em parênteses ou sem separação."""
    erros = []
    # Procura por siglas entre parênteses, que é um erro
    padrao_parenteses = r'\([A-Z]{2,}\)'
    for match in re.finditer(padrao_parenteses, texto_completo):
        erros.append(f"A sigla '{match.group(0)}' não deve estar entre parênteses. Use um travessão (–).")
    
    # Procura por um caso específico comum de erro
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("A sigla 'FDCO' não está separada por travessão. O correto seria '...Centro-Oeste – FDCO'.")
        
    if not erros:
        return {"status": "OK", "detalhe": "A formatação das siglas está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_alineas(texto_completo):
    """(REGRA - Resolução) Verifica a sequência e a pontuação das Alíneas (a, b, c...)."""
    erros = []
    
    # Encontra todos os blocos de alíneas no texto
    blocos_alineas = re.finditer(r'((?:\n\s*[a-z]\).*?)+)', texto_completo)
    
    found_any_block = False
    for bloco in blocos_alineas:
        found_any_block = True
        # Pega todas as alíneas dentro de um bloco, capturando a letra
        alineas = re.findall(r'\n\s*([a-z])\)(.*)', bloco.group(1))
        
        if not alineas:
            continue

        num_alineas = len(alineas)
        expected_char_ord = ord('a')

        for i, (letra_alinea, texto_alinea) in enumerate(alineas):
            alinea_limpa = f"{letra_alinea}) {texto_alinea.strip()}"
            
            # 1. Verificar sequência
            current_char_ord = ord(letra_alinea)
            if current_char_ord != expected_char_ord:
                 erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(expected_char_ord)})', mas encontrado '{letra_alinea})'.")
            expected_char_ord += 1

            # 2. Verificar pontuação
            is_last = (i == num_alineas - 1)
            is_penultimate = (i == num_alineas - 2)
            
            if is_last:
                if not alinea_limpa.endswith('.'):
                    erros.append(f"A última alínea ('{letra_alinea})') deve terminar com ponto final (.).")
            elif is_penultimate:
                if not alinea_limpa.endswith('; e'):
                     erros.append(f"A penúltima alínea ('{letra_alinea})') deve terminar com '; e'.")
            else:
                if not alinea_limpa.endswith(';'):
                    erros.append(f"A alínea intermediária ('{letra_alinea})') deve terminar com ponto e vírgula (;).")

    if not erros:
        if found_any_block:
            return {"status": "OK", "detalhe": "A sequência e pontuação das alíneas estão corretas."}
        else:
            return {"status": "OK", "detalhe": "Nenhuma alínea (a, b, c...) foi encontrada para análise."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_espacamento_paragrafo(texto_completo):
    """(REGRA - Resolução e Anexo) Verifica os 2 espaços após o '§' que INICIA uma linha."""
    
    erros = []
    padrao_esperado = "§  " 

    # Regex agora só busca '§' no INÍCIO da linha (com re.MULTILINE)
    for match in re.finditer(r'^\s*§', texto_completo, re.MULTILINE):
        # Pega o texto a partir do '§' (ignorando a indentação)
        # Encontra a posição do § dentro do match (ex: em "\t\t§")
        pos_simbolo_no_match = match.group(0).rfind('§')
        # Calcula a posição real do § no texto completo
        pos_inicio_match = match.start() + pos_simbolo_no_match
        
        trecho_encontrado = texto_completo[pos_inicio_match : min(pos_inicio_match + 3, len(texto_completo))]

        if len(trecho_encontrado) < 3 or trecho_encontrado != padrao_esperado:
            contexto_curto = texto_completo[pos_inicio_match : min(pos_inicio_match + 15, len(texto_completo))]
            contexto_curto = contexto_curto.split('\n')[0].strip() # Pega só a primeira linha do contexto

            msg = f"Espaçamento incorreto após '§': '{contexto_curto}...'. Esperado: '§  '."
            erros.append(msg)

    if not erros:
        return {"status": "OK", "detalhe": "O espaçamento após o símbolo de parágrafo (§ no início de linha) está correto."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}
    
def auditar_data_sem_zero_esquerda(texto_completo):
    """
    (REGRA - Resolução e Anexo)
    Verifica se as datas no formato 'dd de mes de aaaa' estão
    usando zero à esquerda para dias < 10 (ex: '09 de...').
    """
    erros = []
    
    padrao_data = re.compile(
        r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+)\s+de\s+(\d{4})",
        re.IGNORECASE
    )

    meses_validos = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]

    for match in re.finditer(padrao_data, texto_completo):
        dia_str, mes_str, ano_str = match.groups()
        
        if mes_str.lower() not in meses_validos:
            continue

        if len(dia_str) == 2 and dia_str.startswith('0'):
            dia_correto = str(int(dia_str)) 
            sugestao = f"'{dia_correto} de {mes_str} de {ano_str}'"
            erro_msg = f"Data com dia formatado incorretamente (zero à esquerda): '{match.group(0)}'. O correto seria: {sugestao}."
            erros.append(erro_msg)

    if not erros:
        return {"status": "OK", "detalhe": "Nenhuma data com formatação de dia incorreta (zero à esquerda) foi encontrada."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}


# --- NOVAS REGRAS PARA O ANEXO ---

def auditar_sequencia_capitulos_anexo(texto_completo):
    """(NOVA REGRA - Anexo) Verifica a sequência dos Capítulos (I, II, III...)."""
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
            expected_numeral = current_numeral # Re-sincroniza
        
        expected_numeral += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Capítulos está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_secoes_anexo(texto_completo):
    """(NOVA REGRA - Anexo) Verifica a sequência das Seções (I, II, III...) dentro de cada Capítulo."""
    erros = []
    # Divide o texto por Capítulos para analisar as seções de cada um
    blocos_capitulo = re.split(r'^\s*CAPÍTULO\s+[IVXLCDM]+', texto_completo, flags=re.MULTILINE)
    
    capitulos_encontrados = re.findall(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    
    # O primeiro bloco é o texto *antes* do CAPÍTULO I, então pulamos
    for i, bloco_texto in enumerate(blocos_capitulo[1:]):
        # Pega o nome do capítulo atual para usar na msg de erro
        nome_capitulo = capitulos_encontrados[i] if i < len(capitulos_encontrados) else 'desconhecido'
        
        matches = re.finditer(r'^\s*Seção\s+([IVXLCDM]+)', bloco_texto, re.MULTILINE)
        secoes = [match.group(1) for match in matches]
        
        if not secoes:
            continue # Capítulo pode não ter seções, o que é OK

        expected_numeral = 1
        for numeral_romano in secoes:
            current_numeral = _roman_to_int(numeral_romano)
            
            if current_numeral != expected_numeral:
                erro = f"Sequência de Seções incorreta dentro do CAPÍTULO {nome_capitulo}. Esperado Seção de valor {expected_numeral} (Romano), mas encontrado '{numeral_romano}'."
                erros.append(erro)
                expected_numeral = current_numeral # Re-sincroniza
            
            expected_numeral += 1
            
    if not erros:
        return {"status": "OK", "detalhe": "A sequência das Seções (reiniciando por Capítulo) está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_artigos_anexo(texto_completo):
    """(NOVA REGRA - Anexo) Verifica se a sequência de Artigos (1, 2, 3...) está correta (contínua)."""
    erros = []
    matches = re.finditer(r'Art\.\s*(\d+)', texto_completo)
    artigos = [int(match.group(1)) for match in matches]
    
    if not artigos:
        return {"status": "OK", "detalhe": "Nenhum Artigo encontrado no Anexo para análise de sequência."}

    # No Anexo do exemplo, a contagem é contínua e começa em 1.
    expected_num = 1
    if artigos[0] != 1:
        erros.append(f"O primeiro Artigo do Anexo não é 'Art. 1º'. Encontrado: 'Art. {artigos[0]}'.")
        expected_num = artigos[0]

    for num in artigos:
        if num != expected_num:
            erros.append(f"Sequência de Artigos incorreta no Anexo. Esperado 'Art. {expected_num}', mas encontrado 'Art. {num}'.")
            expected_num = num # Re-sincroniza
        expected_num += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Artigos no Anexo está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_hierarquica_anexo(texto_completo):
    """
    (NOVA REGRA - Anexo) Verifica a pontuação hierárquica (Regras A, B, C)
    de Artigos, Parágrafos, Incisos e Alíneas.
    """
    erros = []
    
    # Padrão para encontrar *todos* os itens estruturais
    padrao_itens = re.compile(
        # Aceita º, ° ou . para art/§
        r"^(?:[ \t]*)((Art\.\s*\d+[º°\.]|Parágrafo\s+único\.|§\s*\d+[º°\.])|([IVXLCDM]+[\s\-–])|([a-z]\)))(.*)", 
        re.MULTILINE | re.IGNORECASE
    )
    
    matches = list(re.finditer(padrao_itens, texto_completo))
    
    for i, match in enumerate(matches):
        linha_completa = match.group(0).strip()
        marcador_item = match.group(1).strip()
        
        # Ignora linhas de CAPÍTULO ou Seção (que podem ser pegas por 'I -')
        if re.match(r'^CAPÍTULO', linha_completa, re.I) or re.match(r'^Seção', linha_completa, re.I):
            continue
            
        # Determina o tipo do item atual
        tipo_atual = None
        if re.match(r'Art\.|Parágrafo|§', marcador_item, re.I):
            tipo_atual = "Artigo/Paragrafo"
        elif re.match(r'^[IVXLCDM]+', marcador_item):
            tipo_atual = "Inciso"
        elif re.match(r'^[a-z]\)', marcador_item):
            tipo_atual = "Alinea"

        # Pega o próximo item, se existir
        proximo_match = matches[i + 1] if (i + 1) < len(matches) else None
        
        # --- REGRA 1: ABERTURA (Dois-Pontos ':') ---
        inicia_subdivisao = False
        if proximo_match:
            marcador_proximo = proximo_match.group(1).strip()
            
            if tipo_atual == "Artigo/Paragrafo" and re.match(r'^[IVXLCDM]+', marcador_proximo):
                inicia_subdivisao = True # Art/§ seguido por Inciso
            elif tipo_atual == "Inciso" and re.match(r'^[a-z]\)', marcador_proximo):
                inicia_subdivisao = True # Inciso seguido por Alínea
        
        if inicia_subdivisao:
            if not linha_completa.endswith(':'):
                erros.append(f"Pontuação de Abertura Incorreta: '{linha_completa}' deve terminar com ':' pois é seguido por uma subdivisão.")
            continue # Regra 1 verificada, pular para o próximo item
            
        # --- REGRAS 2 (Declaração) e 3 (Lista) ---
        
        # Itens do tipo Artigo/Parágrafo (Regra C: Declaração)
        if tipo_atual == "Artigo/Paragrafo":
            if not linha_completa.endswith('.'):
                erros.append(f"Pontuação de Declaração Incorreta: '{linha_completa}' deve terminar com '.'.")
            continue
            
        # Itens do tipo Inciso ou Alínea (Regra B: Lista)
        if tipo_atual in ("Inciso", "Alinea"):
            
            # Pega o tipo do próximo item
            tipo_proximo = None
            if proximo_match:
                marcador_proximo = proximo_match.group(1).strip()
                if re.match(r'Art\.|Parágrafo|§', marcador_proximo, re.I):
                    tipo_proximo = "Artigo/Paragrafo"
                elif re.match(r'^[IVXLCDM]+', marcador_proximo):
                    tipo_proximo = "Inciso"
                elif re.match(r'^[a-z]\)', marcador_proximo):
                    tipo_proximo = "Alinea"

            # --- LÓGICA CORRIGIDA (BASEADA NO SEU ÚLTIMO EXEMPLO) ---
            
            # Se o próximo item é do *mesmo* tipo (ex: Inciso I -> Inciso II)
            # OU se é uma Alínea seguida por um Inciso (ex: b) -> VIII -)
            if (proximo_match and tipo_proximo == tipo_atual) or \
               (tipo_atual == "Alinea" and tipo_proximo == "Inciso"):
                
                # É um item intermediário OU penúltimo.
                # Deve terminar com ';', '; e', ou '; ou'.
                if not (linha_completa.endswith(';') or linha_completa.endswith('; e') or linha_completa.endswith('; ou')):
                    erros.append(f"Pontuação de Lista Incorreta: '{linha_completa}' deve terminar com ';', '; e', ou '; ou'.")

            # Se é o último item da lista (não há próximo item, ou o próximo é de tipo MAIOR, como Artigo/Parágrafo)
            else:
                # É o item final da lista. Deve terminar com '.'
                if not linha_completa.endswith('.'):
                    erros.append(f"Pontuação de Fim de Lista Incorreta: '{linha_completa}' deveria terminar com '.' (ponto final), pois é o último item do seu bloco.")
            # --- FIM DA CORREÇÃO ---

    if not erros:
        return {"status": "OK", "detalhe": "A pontuação hierárquica do Anexo está correta."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}