import re

def _roman_to_int(s):
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

def _normalizar(texto):
    if not texto:
        return ""
    return " ".join(texto.split()).upper()

def _obter_contexto(texto, match):
    inicio = match.start()
    return texto[inicio : inicio+60] + '...'

def _calcular_trecho_sujo(texto_completo, pos_inicio_match, pos_fim_match):
    
    resto = texto_completo[pos_fim_match:]
    match_separador = re.match(r'^[\. \tº°ᵒ]*', resto)
    tamanho_extra = len(match_separador.group(0)) if match_separador else 0
    return texto_completo[pos_inicio_match : pos_fim_match + tamanho_extra]

def limpar_para_validar(t):
        if not t: return ""
        return re.sub(r'[^A-Z0-9]', '', t.upper())
