# core/regras/regras_corpo.py
import re

def auditar_considerando(texto_completo):
    """Verifica se a seção 'CONSIDERANDO' existe e está em maiúsculas."""
    match = re.search(r'\n\s*CONSIDERANDO', texto_completo)
    if match:
        return {"status": "OK", "detalhe": "Seção 'CONSIDERANDO' encontrada e formatada corretamente (R004)."}
    else:
        match_case_insensitive = re.search(r'\n\s*considerando', texto_completo, re.IGNORECASE)
        if match_case_insensitive:
            return {"status": "FALHA", "detalhe": ["ERRO R004: A palavra 'Considerando' foi encontrada, mas deve estar em letras maiúsculas ('CONSIDERANDO')."]}
        else:
            return {"status": "FALHA", "detalhe": ["ERRO R004: A seção obrigatória 'CONSIDERANDO' não foi encontrada no documento."]}

def auditar_numeracao_artigos(texto_completo):
    """Verifica se artigos 1º a 9º usam ordinal (º) e se 10 em diante usam cardinal (sem º)."""
    erros = []
    padrao_A = r'(Art\. [1-9])(?![º\s])'
    for match in re.finditer(padrao_A, texto_completo):
        erros.append(f"ERRO R005A: '{match.group(1)}' - Artigo de 1 a 9 deve usar o indicador ordinal 'º' (ex: Art. 1º).")
    padrao_B = r'(Art\. \d{2,})º'
    for match in re.finditer(padrao_B, texto_completo):
        erros.append(f"ERRO R005B: '{match.group(1)}º' - Artigo a partir do 10 deve ser cardinal (sem 'º', ex: Art. 10).")
    if not erros:
        return {"status": "OK", "detalhe": "Numeração ordinal/cardinal dos artigos está correta (R005)."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_incisos(texto_completo):
    """Verifica a pontuação de Incisos (I, II, ...), se eles existirem."""
    erros = []
    incisos = re.findall(r'(^[ \t]*[IVXLCDM]+\s*–.*?(?=\n[ \t]*[IVXLCDM]+\s*–|\Z))', texto_completo, re.MULTILINE | re.DOTALL)
    if not incisos:
        return {"status": "OK", "detalhe": "Nenhum inciso (I-, II-, etc.) encontrado para auditoria (R008)."}
    num_incisos = len(incisos)
    for i, inciso_texto in enumerate(incisos):
        e_ultimo = (i == num_incisos - 1)
        terminacao_atual = inciso_texto.strip()[-1]
        numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_texto.strip()).group(1)
        tem_alineas = re.search(r':\s*\n\s*[a-z]\)', inciso_texto)
        if e_ultimo:
            if terminacao_atual != '.':
                erros.append(f"ERRO R008C: Último inciso da sequência (Inciso {numeral_romano}) deve terminar com PONTO (.). Terminação atual: '{terminacao_atual}'")
        else:
            if tem_alineas and terminacao_atual != ':':
                erros.append(f"ERRO R008B: Inciso {numeral_romano} tem alíneas, mas não termina com DOIS PONTOS (:). Terminação atual: '{terminacao_atual}'")
            elif not tem_alineas and terminacao_atual != ';':
                erros.append(f"ERRO R008A: Inciso {numeral_romano} deve terminar com PONTO E VÍRGULA (;). Terminação atual: '{terminacao_atual}'")
    if not erros:
        return {"status": "OK", "detalhe": "Pontuação dos incisos está conforme a regra (R008)."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_uso_siglas(texto_completo):
    """Verifica se as siglas estão usando travessão ou se estão incorretamente em parênteses ou sem separação."""
    erros = []
    padrao_parenteses = r'\([A-Z]{2,}\)'
    for match in re.finditer(padrao_parenteses, texto_completo):
        erros.append(f"ERRO R010A: Sigla entre parênteses encontrada: '{match.group(0)}'. Use travessão (–) em seu lugar.")
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("ERRO R010B: 'Centro-Oeste FDCO' - A sigla não está separada por travessão. O correto seria 'Centro-Oeste – FDCO'.")
    if not erros:
        return {"status": "OK", "detalhe": "Uso de siglas está conforme a regra (R010)."}
    else:
        return {"status": "FALHA", "detalhe": erros}