import re
import locale
from datetime import datetime

def auditar_fecho_vigencia(texto_completo):
    """
    Verifica se a cláusula de vigência corresponde exatamente a um dos padrões:
    1. Esta Resolução entra em vigor na data de sua publicação.
    2. Esta Resolução entra em vigor em [dia]º de [mês] de [ano]. (Mês em minúsculo)
    """
    texto_para_analise = texto_completo
    erros = [] # Lista para armazenar erros de validação de data

    match_anexo = re.search(r'\n\s*ANEXO', texto_para_analise, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_para_analise[:match_anexo.start()]

    # Padrão 1: Data de publicação (Exato, com ponto final)
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
             # Continua para verificar o Padrão 2

    # Padrão 2: Data específica (Exato, com ordinal º ou °, mês minúsculo, ponto final)
    padrao_data_especifica_regex = re.compile(
        r"(Esta\s+Resolução\s+entra\s+em\s+vigor\s+em\s+" # Início Fixo
        r"(\d{1,2})[º°]\s+de\s+" # Dia com ordinal (º) ou grau (°)
        r"([a-záçãõéêíóôú]+)\s+de\s+" # Mês (minúsculo com acentos comuns)
        r"(\d{4})\.)" # Ano com ponto final
    )
    match_data = padrao_data_especifica_regex.search(texto_para_analise)

    if match_data:
        frase_completa, dia_str, mes_str, ano_str = match_data.groups()
        frase_encontrada = re.sub(r'\s+', ' ', frase_completa).strip()

        # Valida a data encontrada
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            data_str_validacao = f"{dia_str} de {mes_str} de {ano_str}" # Mês já está minúsculo pela regex
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
        msg_falha = ("A cláusula de vigência não foi encontrada ou não segue um dos padrões exatos esperados: "
                     "'Esta Resolução entra em vigor na data de sua publicação.' ou "
                     "'Esta Resolução entra em vigor em [dia]° de [mês minúsculo] de [ano].'")
        erros.append(msg_falha)

    return {"status": "FALHA", "detalhe": erros}


def auditar_assinatura(texto_completo):
    """
    Verifica se o bloco de assinatura segue o novo padrão (APENAS NOME EM MAIÚSCULAS).
    """
    
    texto_para_analise = texto_completo
    
    # Procura pelo início do anexo para delimitar o fim da resolução
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        # Se encontrou um anexo, analisa apenas o texto ANTES dele
        texto_para_analise = texto_completo[:match_anexo.start()]

    # Pega as últimas 4 linhas não vazias para análise
    linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
    
    if not linhas:
        return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
    # Analisa as últimas 4 linhas para mais robustez (ou menos, se o doc for curto)
    ultimas_linhas = linhas[-4:] 
    
    indice_nome = -1
    linha_nome = ""

    # Encontra a linha do NOME (toda maiúscula, mais de uma palavra)
    for i, linha in enumerate(ultimas_linhas):
        if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
            indice_nome = i
            linha_nome = linha
            break
    
    if indice_nome == -1:
        return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
    
    # Verifica se a linha do nome NÃO é a última linha do bloco
    # Se não for a última, significa que há algo abaixo dela, o que é um erro.
    if indice_nome < len(ultimas_linhas) - 1:
        linha_seguinte = ultimas_linhas[indice_nome + 1]
        return {"status": "FALHA", "detalhe": [f"O bloco de assinatura deve conter apenas o nome em maiúsculas ('{linha_nome}'). Foi encontrado texto abaixo dele: '{linha_seguinte}'."]}
    
    # Se for a última linha (indice_nome == len(ultimas_linhas) - 1), está correto.
    return {"status": "OK", "detalhe": "O bloco de assinatura (apenas nome) está formatado corretamente."}