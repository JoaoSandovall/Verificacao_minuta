import re
import locale
from datetime import datetime
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
    """Verifica parágrafos (§). Aceita '§ 10' sem ponto."""
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
    """Verifica datas com zero à esquerda."""
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

# --- REGRAS DE CONTEÚDO COMUM (EMENTA, VIGÊNCIA, ASSINATURA) ---

def auditar_ementa(texto_completo):
    """Verifica verbo inicial da ementa."""
    VERBOS_ACEITOS = ["Aprova", "Altera", "Dispõe", "Regulamenta", "Define", "Estabelece", "Autoriza", "Prorroga", "Revoga", "Atualização"]
    try:
        padrao_epigrafe = re.compile(r".* DE \d{4}", re.IGNORECASE)
        match_epigrafe = padrao_epigrafe.search(texto_completo)
        if not match_epigrafe:
            return {"status": "FALHA", "detalhe": ["Não foi possível encontrar a ementa pois a linha da data (epígrafe) não foi localizada."]}
        
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():]
        linhas_ementa = texto_apos_epigrafe.strip().split('\n')
        texto_ementa = ""
        for linha in linhas_ementa:
            if linha.strip():
                texto_ementa = linha.strip()
                break
        if not texto_ementa:
            return {"status": "FALHA", "detalhe": ["Não foi possível encontrar o texto da ementa após a data."]}
        
        primeira_palavra = texto_ementa.split()[0]
        if primeira_palavra in VERBOS_ACEITOS:
            return {"status": "OK", "detalhe": f"A ementa inicia corretamente com o verbo '{primeira_palavra}'."}
        else:
            return {"status": "FALHA", "detalhe": [f"A ementa deve começar com um verbo de ação (ex: Aprova, Altera), mas começou com '{primeira_palavra}'."]}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["A ementa parece estar vazia ou com formatação inválida."]}

def auditar_assinatura(texto_completo):
    """Verifica assinatura (Apenas nome em maiúsculo)."""
    texto_para_analise = texto_completo
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_completo[:match_anexo.start()]

    linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
    if not linhas:
        return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
    ultimas_linhas = linhas[-4:] 
    indice_nome = -1
    linha_nome = ""

    for i, linha in enumerate(ultimas_linhas):
        if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
            indice_nome = i
            linha_nome = linha
            break
    
    if indice_nome == -1:
        return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
    
    if indice_nome < len(ultimas_linhas) - 1:
        linha_seguinte = ultimas_linhas[indice_nome + 1]
        return {"status": "FALHA", "detalhe": [f"O bloco de assinatura deve conter apenas o nome em maiúsculas ('{linha_nome}'). Foi encontrado texto abaixo dele: '{linha_seguinte}'."]}
    
    return {"status": "OK", "detalhe": "O bloco de assinatura (apenas nome) está formatado corretamente."}

def auditar_fecho_vigencia(texto_completo):
    """Verifica cláusula de vigência."""
    texto_para_analise = texto_completo
    match_anexo = re.search(r'\n\s*ANEXO', texto_para_analise, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_para_analise[:match_anexo.start()]

    erros = []
    padrao_publicacao_texto = "Esta Resolução entra em vigor na data de sua publicação."
    padrao_publicacao_regex = re.compile(r"Esta\s+Resolução\s+entra\s+em\s+vigor\s+na\s+data\s+de\s+sua\s+publicação\.", re.IGNORECASE)
    match_publicacao = padrao_publicacao_regex.search(texto_para_analise)

    if match_publicacao:
        frase_encontrada = re.sub(r'\s+', ' ', match_publicacao.group(0)).strip()
        frase_esperada_normalizada = re.sub(r'\s+', ' ', padrao_publicacao_texto).strip()
        if frase_encontrada.lower() == frase_esperada_normalizada.lower():
             return {"status": "OK", "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"}
        else:
             erros.append(f"Encontrado texto similar, mas não exato '{padrao_publicacao_texto}'. Encontrado: '{frase_encontrada}'")

    padrao_data_especifica_regex = re.compile(
        r"(Esta\s+Resolução\s+entra\s+em\s+vigor\s+em\s+"
        r"(\d{1,2})[º°]\s+de\s+"
        r"([a-záçãõéêíóôú]+)\s+de\s+"
        r"(\d{4})\.)"
    )
    match_data = padrao_data_especifica_regex.search(texto_para_analise)

    if match_data:
        frase_completa, dia_str, mes_str, ano_str = match_data.groups()
        frase_encontrada = re.sub(r'\s+', ' ', frase_completa).strip()

        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            data_str_validacao = f"{dia_str} de {mes_str} de {ano_str}"
            datetime.strptime(data_str_validacao, "%d de %B de %Y")
            return {
                "status": "OK",
                "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"
            }
        except ValueError:
             return {
                 "status": "FALHA",
                 "detalhe": [f"A data de vigência '{dia_str}º de {mes_str} de {ano_str}' parece ser inválida."]
             }
        except locale.Error:
              return {
                 "status": "OK",
                 "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'. Aviso: Não foi possível validar a data (locale pt_BR não encontrado)."
             }

    if not erros:
        erros.append("A cláusula de vigência não foi encontrada ou não segue um dos padrões exatos esperados.")
    return {"status": "FALHA", "detalhe": erros}

# --- REGRAS DE PONTUAÇÃO ESTRITA (Incisos/Alíneas) ---

def auditar_pontuacao_incisos(texto_completo):
    """(REGRA ESTRITA) Verifica a sequência e pontuação de Incisos."""
    erros = []
    incisos = re.findall(r'(^[ \t]*[IVXLCDM]+[\s\-–].*?)(?=\n[ \t]*[IVXLCDM]+[\s\-–]|\Z)', texto_completo, re.MULTILINE | re.DOTALL)
    
    if not incisos:
        return {"status": "OK", "detalhe": "Nenhum inciso (I, II, etc.) foi encontrado para análise."}
    
    num_incisos = len(incisos)
    expected_numeral = 1

    for i, inciso_texto in enumerate(incisos):
        inciso_limpo = inciso_texto.strip()
        numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_limpo).group(1)
        
        current_numeral = _roman_to_int(numeral_romano)
        if current_numeral != expected_numeral:
            erros.append(f"Sequência de incisos incorreta. Esperado inciso de valor {expected_numeral}, mas encontrado '{numeral_romano}'.")
        expected_numeral += 1

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
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_pontuacao_alineas(texto_completo):
    """(REGRA ESTRITA) Verifica a sequência e pontuação das Alíneas."""
    erros = []
    blocos_alineas = re.finditer(r'((?:\n\s*[a-z]\).*?)+)', texto_completo)
    
    found_any_block = False
    for bloco in blocos_alineas:
        found_any_block = True
        alineas = re.findall(r'\n\s*([a-z])\)(.*)', bloco.group(1))
        
        if not alineas:
            continue

        num_alineas = len(alineas)
        expected_char_ord = ord('a')

        for i, (letra_alinea, texto_alinea) in enumerate(alineas):
            alinea_limpa = f"{letra_alinea}) {texto_alinea.strip()}"
            current_char_ord = ord(letra_alinea)
            if current_char_ord != expected_char_ord:
                 erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(expected_char_ord)})', mas encontrado '{letra_alinea})'.")
            expected_char_ord += 1

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