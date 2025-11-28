import re
from core.utils import _roman_to_int

def _obter_contexto(texto, match):
    """Retorna a linha inteira do match para exibir no erro."""
    inicio = match.start()
    fim = texto.find('\n', inicio)
    if fim == -1:
        fim = len(texto)
    
    trecho = texto[inicio:fim].strip()
    return trecho[:60] + "..." if len(trecho) > 60 else trecho

# --- REGRAS DE ESTRUTURA GERAL ---

def auditar_numeracao_artigos(texto_completo):
    """Verifica a numeração e o espaçamento dos artigos que INICIAM uma linha."""
    erros = []
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        pos_fim_match = match.end()
        
        # Obtém o contexto usando a função auxiliar segura
        contexto = _obter_contexto(texto_completo, match)
        
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        if 1 <= numero_artigo <= 9:
            padrao_esperado = "ᵒ  " 
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('º') or trecho_apos_artigo.startswith('°'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use 'ᵒ'. Trecho: '{contexto}'")
                elif not trecho_apos_artigo.startswith('ᵒ'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal 'ᵒ'. Trecho: '{contexto}'")
                elif not trecho_apos_artigo.startswith('ᵒ  '):
                    erros.append(f"Após 'Art. {numero_artigo}ᵒ', deve haver dois espaços. Trecho: '{contexto}'")
        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            if not trecho_apos_artigo.startswith(padrao_esperado):
                if trecho_apos_artigo.startswith('°') or trecho_apos_artigo.startswith('º') or trecho_apos_artigo.startswith('ᵒ'):
                    erros.append(f"O 'Art. {numero_artigo}' deve usar ponto final (.), não ordinal. Trecho: '{contexto}'")
                elif not trecho_apos_artigo.startswith('.'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido por ponto (.). Trecho: '{contexto}'")
                elif not trecho_apos_artigo.startswith('.  '):
                     erros.append(f"Após 'Art. {numero_artigo}.', deve haver dois espaços. Trecho: '{contexto}'")

    if not erros:
        return {"status": "OK", "detalhe": "A numeração e espaçamento dos artigos estão corretos."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:10]}

def auditar_espacamento_paragrafo(texto_completo):
    """Verifica parágrafos (§). Aceita '§ 10' sem ponto. Usa 'ᵒ'."""
    erros = []
    matches_numerados = re.finditer(r'^\s*§\s+(\d+)', texto_completo, re.MULTILINE)

    for match in matches_numerados:
        numero_paragrafo_str = match.group(1)
        numero_paragrafo = int(numero_paragrafo_str)
        pos_fim_match = match.end()
        
        # Obtém o contexto usando a função auxiliar segura
        contexto = _obter_contexto(texto_completo, match)
        
        trecho_apos_numero = texto_completo[pos_fim_match : pos_fim_match + 3]

        if 1 <= numero_paragrafo <= 9:
            if not trecho_apos_numero.startswith("ᵒ  "):
                erros.append(f"O '§ {numero_paragrafo}' deve ter 'ᵒ' e dois espaços. Trecho: '{contexto}'")

        elif numero_paragrafo >= 10:
            if trecho_apos_numero.startswith('°') or trecho_apos_numero.startswith('º') or trecho_apos_numero.startswith('ᵒ'):
                 erros.append(f"O '§ {numero_paragrafo}' não deve usar ordinal. Trecho: '{contexto}'")
            elif trecho_apos_numero.startswith('.'):
                if not trecho_apos_numero.startswith('.  '):
                    erros.append(f"Após '§ {numero_paragrafo}.', deve haver dois espaços. Trecho: '{contexto}'")
            elif trecho_apos_numero.startswith(' '):
                if not trecho_apos_numero.startswith('  '):
                     erros.append(f"Após '§ {numero_paragrafo}' (sem ponto), deve haver dois espaços. Trecho: '{contexto}'")
            else:
                erros.append(f"Formatação inválida após '§ {numero_paragrafo}'. Trecho: '{contexto}'")

    matches_unicos = re.finditer(r'^\s*Parágrafo\s+único\.', texto_completo, re.MULTILINE)
    for match in matches_unicos:
        pos_fim_match = match.end()
        contexto = _obter_contexto(texto_completo, match)
        
        if not texto_completo[pos_fim_match : pos_fim_match + 2] == "  ":
            erros.append(f"Após 'Parágrafo único.', deve haver dois espaços. Trecho: '{contexto}'")

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
    """Verifica cláusula de vigência. Aceita 'ᵒ'."""
    if "Esta Resolução entra em vigor" not in texto_completo:
         return {"status": "FALHA", "detalhe": ["Cláusula de vigência não encontrada."]}
    
    # Valida ordinal na vigência
    busca_errada = re.search(r"entra\s+em\s+vigor\s+em\s+\d{1,2}[º°]\s+de", texto_completo)
    if busca_errada:
        return {"status": "FALHA", "detalhe": [f"Data de vigência usando ordinal incorreto. Use 'ᵒ'. Trecho: '{busca_errada.group(0)}'"]}

    return {"status": "OK", "detalhe": "Vigência encontrada."}

def auditar_pontuacao_incisos(texto_completo):

    erros = []
    
    # Regex: Exige traço (incluindo travessão —) e para antes de estruturas
    padrao_inciso = re.compile(
        r'(^[ \t]*[IVXLCDM]+\s*[\-–—].*?)(?=\n\s*(?:[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)|$)', 
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
        
        # Contexto limpo (remove quebras de linha para exibição)
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
        pos_fim = match.end()
        proximo_trecho = texto_completo[pos_fim:pos_fim+200].lstrip()
        
        # Lookahead com travessão
        if re.match(r'[IVXLCDM]+\s*[\-–—]', proximo_trecho): is_last_in_list = False
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)', proximo_trecho): is_last_in_list = True
        elif not proximo_trecho: is_last_in_list = True
        else: is_last_in_list = True

        if inciso_texto.endswith(':'): continue

        if is_last_in_list:
            if not inciso_texto.endswith('.'):
                erros.append(f"O último inciso do bloco ({numeral_romano}) deve terminar com ponto final (.). Trecho: '{trecho_limpo}'")
        else:
            if not (inciso_texto.endswith(';') or inciso_texto.endswith('; e') or inciso_texto.endswith('; ou')):
                erros.append(f"O inciso intermediário ({numeral_romano}) deve terminar com ponto e vírgula (;). Trecho: '{trecho_limpo}'")

    if not erros:
        return {"status": "OK", "detalhe": "Pontuação dos incisos correta."}
    return {"status": "FALHA", "detalhe": erros[:10]}

def auditar_pontuacao_alineas(texto_completo):

    erros = []
    
    padrao_alinea = re.compile(
        r'(^\s*[a-z]\).*?)(?=\n\s*(?:[a-z]\)|[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO)|$)', 
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
        
        if letra == 'a':
            pass
        elif i > 0:
            prev_match = matches[i-1]
            prev_texto = prev_match.group(1).strip()
            prev_letra = prev_texto[0]
            gap = texto_completo[prev_match.end():match.start()]
            tem_quebra = re.search(r'(Art\.|§|[IVXLCDM])', gap)
            if not tem_quebra and current_ord != ord(prev_letra) + 1:
                 erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(ord(prev_letra)+1)})', mas encontrado '{letra})'. Trecho: '{trecho_visual}'")

        pos_fim = match.end()
        proximo_trecho = texto_completo[pos_fim:pos_fim+200].lstrip()
        
        is_final_structure = False
        continues_parent = False
        continues_alinea = False

        if re.match(r'[a-z]\)', proximo_trecho): continues_alinea = True
        elif re.match(r'[IVXLCDM]+\s*[\-–—]', proximo_trecho): continues_parent = True
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|ANEXO)', proximo_trecho) or not proximo_trecho: is_final_structure = True
        else: is_final_structure = True

        if is_final_structure:
            if not texto.endswith('.'):
                erros.append(f"A última alínea ('{letra})') deve terminar com ponto final (.). Trecho: '{trecho_visual}'")
        elif continues_parent or continues_alinea:
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                 erros.append(f"A alínea intermediária ('{letra})') deve terminar com ponto e vírgula (;). Trecho: '{trecho_visual}'")

    if not erros: return {"status": "OK", "detalhe": "Alíneas corretas."}
    return {"status": "FALHA", "detalhe": erros[:10]}