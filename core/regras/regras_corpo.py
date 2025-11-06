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
    e na terminação com 'RESOLVE:'.
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
        
        match_artigo1 = re.search(r'Art\.\s*1[ºo]', inicio_preambulo_texto, re.IGNORECASE)
        
        texto_preambulo = inicio_preambulo_texto[:match_artigo1.start()].strip()

    except (AttributeError, IndexError):
        # Retorna o erro no formato de dicionário para manter a consistência
        return {"status": "FALHA", "detalhe": [{"mensagem": "Não foi possível isolar o texto do preâmbulo para análise. Verifique se a ementa e o Art. 1º existem.", "contexto": ""}]}

    if not texto_preambulo:
        return {"status": "FALHA", "detalhe": [{"mensagem": "O texto do preâmbulo parece estar vazio.", "contexto": ""}]}

    # Passo 2: Verificar as regras com a nova lista de autoridades
    autoridades_validas = [
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE - CONDEL/SUDECO",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA - CONDEL/SUDAM",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE – CONDEL/SUDENE"
    ]
    
    # Normaliza o texto do preâmbulo para uma única linha para facilitar a comparação
    # Isso lida com as quebras de linha que podem existir no meio do título
    texto_preambulo_normalizado = re.sub(r'\s+', ' ', texto_preambulo)

    autoridade_encontrada = False
    for autoridade in autoridades_validas:
        autoridade_normalizada = re.sub(r'\s+', ' ', autoridade)
        if texto_preambulo_normalizado.startswith(autoridade_normalizada):
            autoridade_encontrada = True
            break
            
    if not autoridade_encontrada:
        contexto_erro = texto_preambulo.split('\n')[0].strip()
        # Mantém a mensagem de erro simples
        erros.append("mensagem : O Começo do preâmbulo está incorreto.")

    # Regra 2: A palavra 'RESOLVE:' no final, em maiúsculas (lógica antiga)
    # Verifica a última linha não vazia
    ultima_linha = ""
    linhas_preambulo = texto_preambulo.strip().split('\n')
    if linhas_preambulo:
        ultima_linha = linhas_preambulo[-1].strip()

    if ultima_linha != "RESOLVEU:":
        # Mantém as mensagens de erro simples
        if ultima_linha.lower() == "resolveu:":
            erros.append(f"mensagem: a palavra 'RESOLVEU:' no final do preâmbulo deve estar em maiúsculas. E não: '{ultima_linha}'")
        else:
            erros.append(f"mensagem: O preâmbulo deve terminar com a palavra 'RESOLVEU:' Mas foi encontrado: {ultima_linha}")
            
    # Passo 3: Retornar o resultado
    if not erros:
        return {"status": "OK", "detalhe": "O preâmbulo está estruturado corretamente."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_numeracao_artigos(texto_completo):
    """
    Verifica a numeração e o espaçamento dos artigos com regras mais rígidas.
    - Art. 1º a 9º: Deve ser 'Art. N°  ' (com º e dois espaços).
    - Art. 10 em diante: Deve ser 'Art. NN.  ' (com . e dois espaços).
    """
    erros = []
    
    # Encontra todas as ocorrências de "Art. [número]" para análise individual
    matches = re.finditer(r'Art\.\s*(\d+)', texto_completo)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        
        # Pega a fatia do texto original logo após o match para verificar pontuação e espaços
        pos_fim_match = match.end()
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        # --- VALIDAÇÃO PARA ARTIGOS DE 1 A 9 ---
        if 1 <= numero_artigo <= 9:
            padrao_esperado = "º  "
    
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
                if trecho_apos_artigo.startswith('°'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use 'º' em vez de '°'.")
                elif not trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal 'º'.")
                elif not trecho_apos_artigo.startswith('º  '):
                    erros.append(f"Após 'Art. {numero_artigo}º', deve haver exatamente dois espaços.")
                else:
                     erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: 'º' seguido de dois espaços.")

        # --- VALIDAÇÃO PARA ARTIGOS 10 EM DIANTE ---
        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
                if trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' não deve usar o ordinal 'º', mas sim um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido por um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.  '):
                     erros.append(f"Após 'Art. {numero_artigo}.', deve haver exatamente dois espaços.")
                else: # Outros erros de formatação
                    erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: '.' seguido de dois espaços.")

    if not erros:
        return {"status": "OK", "detalhe": "A numeração e espaçamento dos artigos estão corretos."}
    else:
        # Usa list(set(erros)) para remover mensagens de erro duplicadas
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}
    
def auditar_pontuacao_incisos(texto_completo):
    """Verifica a sequência e a pontuação de Incisos (I, II, ...)."""
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
            continue # Pula para o próximo inciso se este tem alíneas

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
    """Verifica se as siglas estão usando travessão ou se estão incorretamente em parênteses ou sem separação."""
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
    """Verifica a sequência e a pontuação das Alíneas (a, b, c...)."""
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
    # Verifica os 2 espaços após o "§"
    
    erros = []
    padrao_paragrafo = r"§"
    padrao_esperado = "§  " 

    # Usamos finditer para encontrar todas as ocorrências
    for match in re.finditer(padrao_paragrafo, texto_completo):
        pos_inicio_match = match.start()
        # Pega os 3 caracteres a partir do § (o próprio § e os dois seguintes)
        # Adiciona verificação para não ir além do fim do texto
        trecho_encontrado = texto_completo[pos_inicio_match : min(pos_inicio_match + 3, len(texto_completo))]

        # Verifica se o trecho encontrado tem pelo menos 3 caracteres (para § e dois espaços)
        # Ou se o § está exatamente no final do texto (o que também seria um erro de espaçamento)
        if len(trecho_encontrado) < 3 or trecho_encontrado != padrao_esperado:
            # Captura um contexto mínimo para identificação do local do erro
            contexto_curto = texto_completo[pos_inicio_match : min(pos_inicio_match + 15, len(texto_completo))]
            contexto_curto = contexto_curto.split('\n')[0].strip() # Pega só a primeira linha do contexto

            msg = f"Espaçamento incorreto após '§': '{contexto_curto}...'. Esperado: '§  '."
            erros.append(msg) # Adiciona mensagem simples com contexto

    if not erros:
        return {"status": "OK", "detalhe": "O espaçamento após o símbolo de parágrafo (§) está correto."}
    else:
        # Retorna lista de strings, limitando a 5 mensagens
        return {"status": "FALHA", "detalhe": erros[:5]}