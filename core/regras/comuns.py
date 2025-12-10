import re
from core.utils import _roman_to_int

def _obter_contexto(texto, match):
    inicio = match.start()
    return texto[inicio : inicio+60] + "..."

def _calcular_trecho_sujo(texto_completo, pos_inicio_match, pos_fim_match):
    
    resto = texto_completo[pos_fim_match:]
    match_separador = re.match(r'^[\. \tº°ᵒ]*', resto)
    tamanho_extra = len(match_separador.group(0)) if match_separador else 0
    return texto_completo[pos_inicio_match : pos_fim_match + tamanho_extra]

# --- REGRAS DE ESTRUTURA ---

def auditar_numeracao_artigos(texto_completo):
    erros = []
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)
    
    for match in matches:
        numero = int(match.group(1))
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        
        # Calcula endereço exato
        trecho_analisado = _calcular_trecho_sujo(texto_completo, match.start(), pos_fim)
        
        trecho_pos = texto_completo[pos_fim : pos_fim + 3]
        if len(trecho_pos) < 3: trecho_pos = trecho_pos.ljust(3)

        msgs_erro = []
        correcao = None

        if 1 <= numero <= 9:
            simbolo = trecho_pos[0]
            espacos = trecho_pos[1:]
            if simbolo != 'ᵒ':
                if simbolo in ['º', '°']: msgs_erro.append(f"símbolo incorreto ('{simbolo}', use 'ᵒ')")
                elif simbolo == '.': msgs_erro.append("uso de ponto final (use 'ᵒ')")
                else: msgs_erro.append(f"símbolo inválido")
            if espacos != '  ': msgs_erro.append("espaçamento incorreto (esperado 2)")
            
            if msgs_erro: correcao = f"Art. {numero}ᵒ  "

        elif numero >= 10:
            simbolo = trecho_pos[0]
            espacos = trecho_pos[1:]
            if simbolo != '.':
                if simbolo in ['º', '°', 'ᵒ']: msgs_erro.append("uso de ordinal (use ponto final)")
                else: msgs_erro.append(f"pontuação incorreta ('{simbolo}')")
            if espacos != '  ': msgs_erro.append("espaçamento incorreto (esperado 2)")
            
            if msgs_erro: correcao = f"Art. {numero}.  "
        
        if msgs_erro:
            texto_msg = " e ".join(msgs_erro)
            texto_msg = texto_msg[0].upper() + texto_msg[1:]
            
            erros.append({
                "mensagem": f"No 'Art. {numero}': {texto_msg}. Trecho: '{contexto}'",
                "original": trecho_analisado,
                "sugestao": correcao,
                "span": [match.start(), match.start() + len(trecho_analisado)], # Endereço
                "tipo": "fixable"
            })
    
    if not erros: return {"status": "OK", "detalhe": "Artigos corretos."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_espacamento_paragrafo(texto_completo):
    erros = []
    
    matches = re.finditer(r'^\s*§\s+(\d+)', texto_completo, re.MULTILINE)
    for match in matches:
        numero = int(match.group(1))
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        
        trecho_analisado = _calcular_trecho_sujo(texto_completo, match.start(), pos_fim)
        
        trecho_pos = texto_completo[pos_fim : pos_fim + 3]
        if len(trecho_pos) < 3: trecho_pos = trecho_pos.ljust(3)

        msgs_erro = []
        correcao = None

        if 1 <= numero <= 9:
            if not trecho_pos.startswith("ᵒ  "):
                msgs_erro.append(f"O '§ {numero}' deve ter 'ᵒ' e dois espaços")
                correcao = f"§ {numero}ᵒ  "

        elif numero >= 10:
            if not trecho_pos.startswith(".  "):
                msgs_erro.append(f"O '§ {numero}' deve ter ponto final e dois espaços")
                correcao = f"§ {numero}.  "

        if msgs_erro:
            erros.append({
                "mensagem": f"{msgs_erro[0]}. Trecho: '{contexto}'",
                "original": trecho_analisado,
                "sugestao": correcao,
                "span": [match.start(), match.start() + len(trecho_analisado)],
                "tipo": "fixable"
            })

    matches_unico = re.finditer(r'^\s*Parágrafo\s+único\.', texto_completo, re.MULTILINE)
    for match in matches_unico:
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        
        trecho_analisado = _calcular_trecho_sujo(texto_completo, match.start(), pos_fim)
        
        trecho_check = texto_completo[pos_fim : pos_fim + 2]
        if trecho_check != "  ":
            erros.append({
                "mensagem": f"Após 'Parágrafo único.', deve haver dois espaços. Trecho: '{contexto}'",
                "original": trecho_analisado,
                "sugestao": "Parágrafo único.  ",
                "span": [match.start(), match.start() + len(trecho_analisado)],
                "tipo": "fixable"
            })

    if not erros: return {"status": "OK", "detalhe": "Parágrafos corretos."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_data_sem_zero_esquerda(texto_completo):
    erros = []
    padrao = re.compile(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+)\s+de\s+(\d{4})", re.IGNORECASE)
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    for match in re.finditer(padrao, texto_completo):
        dia, mes, _ = match.groups()
        if mes.lower() in meses and len(dia) == 2 and dia.startswith('0'):
            erros.append({
                "mensagem": f"Data com zero à esquerda: '{match.group(0)}'. Deve ser '{int(dia)} de {mes}...'",
                "original": match.group(0),
                "tipo": "highlight"
            })
    if not erros: return {"status": "OK", "detalhe": "Datas corretas."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_uso_siglas(texto_completo):
    erros = []
    for match in re.finditer(r'\([A-Z]{2,}\)', texto_completo):
        erros.append(f"Sigla em parênteses: '{match.group(0)}'. Use travessão. Trecho: '{match.group(0)}'")
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("Sigla 'FDCO' sem travessão. Trecho: 'Centro-Oeste FDCO'")
    if not erros: return {"status": "OK", "detalhe": "Siglas corretas."}
    return {"status": "FALHA", "detalhe": erros}

def auditar_ementa(texto_completo):
    match = re.search(r".* DE \d{4}\s*\n+(.*)", texto_completo, re.MULTILINE)
    if match:
        texto = match.group(1).strip()
        verbo = texto.split()[0]
        aceitos = ["Aprova", "Altera", "Dispõe", "Regulamenta", "Define", "Estabelece", "Autoriza", "Prorroga", "Revoga", "Atualização"]
        if verbo not in aceitos:
             return {"status": "FALHA", "detalhe": [f"Verbo incorreto: '{verbo}'. Trecho: '{texto[:30]}...'"]}
    return {"status": "OK", "detalhe": "Ementa correta."}

def auditar_assinatura(texto_completo):
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    texto = texto_completo[:match_anexo.start()] if match_anexo else texto_completo
    linhas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
    if linhas:
        ultimas = linhas[-3:]
        if not any(l.isupper() and len(l) > 5 and " " in l and not l.startswith("Art") for l in ultimas):
             return {"status": "FALHA", "detalhe": ["O bloco de assinatura deve conter o NOME em maiúsculas."]}
    return {"status": "OK", "detalhe": "Assinatura correta."}

def auditar_fecho_vigencia(texto_completo):
    if "Esta Resolução entra em vigor" not in texto_completo:
         return {"status": "FALHA", "detalhe": ["Cláusula de vigência não encontrada."]}
    busca_errada = re.search(r"entra\s+em\s+vigor\s+em\s+\d{1,2}[º°]\s+de", texto_completo)
    if busca_errada:
        return {"status": "FALHA", "detalhe": [f"Ordinal incorreto na vigência. Use 'ᵒ'. Trecho: '{busca_errada.group(0)}'"]}
    return {"status": "OK", "detalhe": "Vigência encontrada."}

def auditar_pontuacao_incisos(texto_completo):
    erros = []
    padrao = re.compile(r'(^[ \t]*[IVXLCDM]+\s*[\-–—].*?)(?=\n\s*(?:[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)|$)', re.MULTILINE | re.DOTALL)
    matches = list(padrao.finditer(texto_completo))
    if not matches: return {"status": "OK", "detalhe": "Nenhum inciso."}
    for i, match in enumerate(matches):
        texto = match.group(1).strip()
        numeral = re.match(r'^\s*([IVXLCDM]+)', texto).group(1)
        val = _roman_to_int(numeral)
        trecho_contexto = texto[:60] + "..."
        if val != 1 and i > 0:
            prev = matches[i-1].group(1).strip()
            prev_rom = re.match(r'^\s*([IVXLCDM]+)', prev).group(1)
            prev_val = _roman_to_int(prev_rom)
            gap = texto_completo[matches[i-1].end():match.start()]
            if not re.search(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo)', gap) and val != prev_val + 1:
                 erros.append(f"Sequência incorreta. Esperado {prev_val + 1}, achou '{numeral}'. Trecho: '{trecho_contexto}'")
        pos_fim = match.end()
        prox = texto_completo[pos_fim:pos_fim+200].lstrip()
        is_last = True
        if re.match(r'[IVXLCDM]+\s*[\-–—]', prox): is_last = False
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)', prox) or not prox: is_last = True
        if texto.endswith(':'): continue
        if is_last:
            if not texto.endswith('.'):
                erros.append(f"Último inciso ({numeral}) sem ponto final. Trecho: '{trecho_contexto}'")
        else:
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                erros.append(f"Inciso intermediário ({numeral}) deve ter ponto e vírgula. Trecho: '{trecho_contexto}'")
    if not erros: return {"status": "OK", "detalhe": "Pontuação incisos correta."}
    return {"status": "FALHA", "detalhe": erros[:50]}

def auditar_pontuacao_alineas(texto_completo):
    erros = []
    padrao = re.compile(r'(^\s*[a-z]\).*?)(?=\n\s*(?:[a-z]\)|[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO)|$)', re.MULTILINE | re.DOTALL)
    matches = list(padrao.finditer(texto_completo))
    if not matches: return {"status": "OK", "detalhe": "Nenhuma alínea."}
    for i, match in enumerate(matches):
        texto = match.group(1).strip()
        letra = texto[0]
        trecho_contexto = texto[:60] + "..."
        ord_letra = ord(letra)
        if letra != 'a' and i > 0:
            prev = matches[i-1].group(1).strip()
            gap = texto_completo[matches[i-1].end():match.start()]
            if not re.search(r'(Art\.|§|[IVXLCDM])', gap) and ord_letra != ord(prev[0]) + 1:
                 erros.append(f"Sequência alíneas incorreta. Achou '{letra})'. Trecho: '{trecho_contexto}'")
        pos_fim = match.end()
        prox = texto_completo[pos_fim:pos_fim+200].lstrip()
        is_final = False
        is_middle = False
        if re.match(r'[a-z]\)', prox): is_middle = True
        elif re.match(r'[IVXLCDM]+\s*[\-–—]', prox): is_middle = True
        elif re.match(r'(Art\.|§|CAPÍTULO|Seção|ANEXO)', prox) or not prox: is_final = True
        else: is_final = True
        if is_final:
            if not texto.endswith('.'):
                erros.append(f"Última alínea ('{letra})') sem ponto final. Trecho: '{trecho_contexto}'")
        elif is_middle:
            if not (texto.endswith(';') or texto.endswith('; e') or texto.endswith('; ou')):
                 erros.append(f"Alínea intermediária ('{letra})') deve ter ponto e vírgula. Trecho: '{trecho_contexto}'")
    if not erros: return {"status": "OK", "detalhe": "Alíneas corretas."}
    return {"status": "FALHA", "detalhe": erros[:50]}