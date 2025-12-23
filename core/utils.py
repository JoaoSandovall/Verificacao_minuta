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

def _normalizar(texto):
    # Remove espaços extras, e usa o uppper para transformar em maiusculo
    if not texto:
        return ""
    return " ".join(texto.split()).upper()

def _obter_contexto(texto, match):
    inicio = match.start()
    return texto[inicio : inicio+60] + '...'