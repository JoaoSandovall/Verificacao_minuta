import re
from core.utils import _roman_to_int

def _obter_contexto(texto, match):
    """Retorna o texto bruto até 60 caracteres."""
    inicio = match.start()
    # Pega até 60 chars ou fim da linha, o que vier primeiro, mas preservando o raw
    # Simplificação: pega 60 chars brutos a partir do inicio
    return texto[inicio : inicio+60] + "..."

# --- REGRAS DE ESTRUTURA ---

def auditar_numeracao_artigos(texto_completo):
    erros = []
    matches = re.finditer(r'^\s*Art\.\s*(\d+)', texto_completo, re.MULTILINE)
    for match in matches:
        numero = int(match.group(1))
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        trecho_pos = texto_completo[pos_fim : pos_fim + 3]

        if 1 <= numero <= 9:
            if not trecho_pos.startswith("ᵒ  "):
                erros.append(f"No 'Art. {numero}', use 'ᵒ' e dois espaços. Trecho: '{contexto}'")
        elif numero >= 10:
            if not trecho_pos.startswith(".  "):
                erros.append(f"No 'Art. {numero}', use ponto final e dois espaços. Trecho: '{contexto}'")
    
    if not erros: return {"status": "OK", "detalhe": "Artigos corretos."}
    return {"status": "FALHA", "detalhe": list(set(erros))[:10]}

def auditar_espacamento_paragrafo(texto_completo):
    erros = []
    matches = re.finditer(r'^\s*§\s+(\d+)', texto_completo, re.MULTILINE)
    for match in matches:
        numero = int(match.group(1))
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        trecho_pos = texto_completo[pos_fim : pos_fim + 3]

        if 1 <= numero <= 9:
            if not trecho_pos.startswith("ᵒ  "):
                erros.append(f"O '§ {numero}' deve ter 'ᵒ' e dois espaços. Trecho: '{contexto}'")
        elif numero >= 10:
            if not (trecho_pos.startswith(".  ") or trecho_pos.startswith("  ")):
                erros.append(f"Formatação inválida após '§ {numero}'. Trecho: '{contexto}'")

    matches_unico = re.finditer(r'^\s*Parágrafo\s+único\.', texto_completo, re.MULTILINE)
    for match in matches_unico:
        pos_fim = match.end()
        contexto = _obter_contexto(texto_completo, match)
        if not texto_completo[pos_fim : pos_fim + 2] == "  ":
            erros.append(f"Após 'Parágrafo único.', deve haver dois espaços. Trecho: '{contexto}'")

    if not erros: return {"status": "OK", "detalhe": "Parágrafos corretos."}
    return {"status": "FALHA", "detalhe": list(set(erros))[:10]}

def auditar_data_sem_zero_esquerda(texto_completo):
    erros = []
    padrao = re.compile(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃõÕáÁéÉíÍóÓúÚ]+)\s+de\s+(\d{4})", re.IGNORECASE)
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    for match in re.finditer(padrao, texto_completo):
        dia, mes, _ = match.groups()
        if mes.lower() in meses and len(dia) == 2 and dia.startswith('0'):
            erros.append(f"Data com zero à esquerda: '{match.group(0)}'.")
    if not erros: return {"status": "OK", "detalhe": "Datas corretas."}
    return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_uso_siglas(texto_completo):
    erros = []
    for match in re.finditer(r'\([A-Z]{2,}\)', texto_completo):
        erros.append(f"Sigla em parênteses: '{match.group(0)}'. Use travessão. Trecho: '{match.group(0)}'")
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("Sigla 'FDCO' sem travessão. Trecho: 'Centro-Oeste FDCO'")
    if not erros: return {"status": "OK", "detalhe": "Siglas corretas."}
    return {"status": "FALHA", "detalhe": erros}

# --- COMUM ---

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

# --- PONTUAÇÃO (CORRIGIDO PARA TEXTO BRUTO) ---

def auditar_pontuacao_incisos(texto_completo):
    erros = []
    padrao = re.compile(r'(^[ \t]*[IVXLCDM]+\s*[\-–—].*?)(?=\n\s*(?:[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO|Seção|Parágrafo|ANEXO)|$)', re.MULTILINE | re.DOTALL)
    matches = list(padrao.finditer(texto_completo))
    
    if not matches: return {"status": "OK", "detalhe": "Nenhum inciso."}

    for i, match in enumerate(matches):
        texto = match.group(1).strip()
        numeral = re.match(r'^\s*([IVXLCDM]+)', texto).group(1)
        val = _roman_to_int(numeral)
        
        # CORREÇÃO: Contexto agora é o texto bruto (limitado a 60), sem re.sub
        # Isso permite que o api.py encontre exatamente essa string no documento
        trecho_contexto = texto[:60] + "..."

        # Sequência
        if val != 1 and i > 0:
            prev = matches[i-1].group(1).strip()
            prev_rom = re.match(r'^\s*([IVXLCDM]+)', prev).group(1)
            prev_val = _roman_to_int(prev_rom)
            gap = texto_completo[matches[i-1].end():match.start()]
            if not re.search(r'(Art\.|§|CAPÍTULO|Seção|Parágrafo)', gap) and val != prev_val + 1:
                 erros.append(f"Sequência incorreta. Esperado {prev_val + 1}, achou '{numeral}'. Trecho: '{trecho_contexto}'")

        # Pontuação
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
    return {"status": "FALHA", "detalhe": erros[:10]}

def auditar_pontuacao_alineas(texto_completo):
    erros = []
    padrao = re.compile(r'(^\s*[a-z]\).*?)(?=\n\s*(?:[a-z]\)|[IVXLCDM]+\s*[\-–—]|Art\.|§|CAPÍTULO)|$)', re.MULTILINE | re.DOTALL)
    matches = list(padrao.finditer(texto_completo))
    
    if not matches: return {"status": "OK", "detalhe": "Nenhuma alínea."}

    for i, match in enumerate(matches):
        texto = match.group(1).strip()
        letra = texto[0]
        # CORREÇÃO: Contexto bruto
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
    return {"status": "FALHA", "detalhe": erros[:10]}