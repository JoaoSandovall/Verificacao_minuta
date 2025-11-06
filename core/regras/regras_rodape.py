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
    # Usamos re.escape para tratar o ponto final literalment
    padrao_publicacao_texto = "Esta Resolução entra em vigor na data de sua publicação."
    # Procuramos o padrão exato, considerando espaços flexíveis (\s+)
    padrao_publicacao_regex = re.compile(r"Esta\s+Resolução\s+entra\s+em\s+vigor\s+na\s+data\s+de\s+sua\s+publicação\.", re.IGNORECASE)
    match_publicacao = padrao_publicacao_regex.search(texto_para_analise)

    if match_publicacao:
        # Verifica se a frase encontrada corresponde exatamente (ignorando múltiplos espaços)
        frase_encontrada = re.sub(r'\s+', ' ', match_publicacao.group(0)).strip()
        frase_esperada_normalizada = re.sub(r'\s+', ' ', padrao_publicacao_texto).strip()
        if frase_encontrada.lower() == frase_esperada_normalizada.lower():
             # Retorna OK se encontrou exatamente
             return {"status": "OK", "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"}
        else:
             # Se encontrou algo parecido mas não exato (raro com essa regex, mas por segurança)
             erros.append(f"Encontrado texto similar, mas não exato '{padrao_publicacao_texto}'. Encontrado: '{frase_encontrada}'")
             # Continua para verificar o Padrão 2

    # Padrão 2: Data específica (Exato, com ordinal º, mês minúsculo, ponto final)
    # Regex para capturar dia(s), mês e ano
    padrao_data_especifica_regex = re.compile(
        r"(Esta\s+Resolução\s+entra\s+em\s+vigor\s+em\s+" # Início Fixo
        r"(\d{1,2})º\s+de\s+" # Dia com ordinal
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
            # Se a data é válida, retorna OK
            return {
                "status": "OK",
                "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"
            }
        except ValueError:
             # Retorna FALHA se a data for inválida
             return {
                 "status": "FALHA",
                 "detalhe": [f"A data de vigência '{dia_str}º de {mes_str} de {ano_str}' parece ser inválida."]
             }
        except locale.Error:
             # Se o locale falhar, aceita a formatação, mas avisa (retorna OK com aviso)
              return {
                 "status": "OK",
                 "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'. Aviso: Não foi possível validar a data (locale pt_BR não encontrado)."
             }

    # Se nenhum dos padrões exatos foi encontrado E não houve erro parcial no padrão 1
    if not erros:
        msg_falha = ("A cláusula de vigência não foi encontrada ou não segue um dos padrões exatos esperados: "
                     "'Esta Resolução entra em vigor na data de sua publicação.' ou "
                     "'Esta Resolução entra em vigor em [dia]º de [mês minúsculo] de [ano].'")
        erros.append(msg_falha)

    # Retorna FALHA se chegou até aqui
    return {"status": "FALHA", "detalhe": erros}


def auditar_assinatura(texto_completo):
    """Verifica se o bloco de assinatura segue o padrão (NOME EM MAIÚSCULAS / Cargo)."""
    
    texto_para_analise = texto_completo
    
    # Procura pelo início do anexo para delimitar o fim da resolução
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        # Se encontrou um anexo, analisa apenas o texto ANTES dele
        texto_para_analise = texto_completo[:match_anexo.start()]

    linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
    
    if len(linhas) < 2:
        return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
    # Analisa as últimas 4 linhas para mais robustez
    ultimas_linhas = linhas[-4:]
    try:
        indice_nome = -1
        for i, linha in enumerate(ultimas_linhas):
            # Procura uma linha que seja MAIÚSCULA, tenha mais de uma palavra e não seja um Artigo
            if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
                indice_nome = i
                break
        
        if indice_nome == -1:
            return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
        
        linha_nome = ultimas_linhas[indice_nome]
        # Pega a linha seguinte à do nome como sendo o cargo
        linha_cargo = ultimas_linhas[indice_nome + 1]
        
        if not linha_cargo or linha_cargo.isupper():
            return {"status": "FALHA", "detalhe": [f"O cargo abaixo do nome '{linha_nome}' não foi encontrado ou está incorretamente em maiúsculas."]}
        
        return {"status": "OK", "detalhe": "O bloco de assinatura está formatado corretamente."}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["A estrutura do bloco de assinatura parece inválida (ex: nome sem cargo abaixo)."]}