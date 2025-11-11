import re
import locale
from datetime import datetime

def auditar_cabecalho_ministerio(texto_completo):
    """Verifica se o nome do ministério está no formato correto no início do documento."""
    padrao_correto = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    if not primeiras_linhas or not primeiras_linhas[0].strip():
        return {"status": "FALHA", "detalhe": ["O documento parece estar vazio ou sem conteúdo."]}
    
    primeira_linha_conteudo = primeiras_linhas[0].strip()
    if primeira_linha_conteudo == padrao_correto:
        return {"status": "OK", "detalhe": "O nome do Ministério está formatado corretamente."}
    else:
        detalhe_erro = f"O nome do Ministério deve ser '{padrao_correto}'. Foi encontrado: '{primeira_linha_conteudo}'."
        return {"status": "FALHA", "detalhe": [detalhe_erro]}


def auditar_epigrafe(texto_completo):
    """
    Verifica se a epígrafe segue o padrão estrito, com tudo em maiúsculas:
    '(MINUTA )?RESOLUÇÃO DE CONDEL Nº [num/xx], DE [dia/xx] DE [MÊS/xx] DE [ano]'
    """
    erros = []
    
    meses_validos = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    
    padrao_epigrafe = re.compile(
        r"(MINUTA )?"
        r"RESOLUÇÃO CONDEL(?:/SUDECO|/SUDENE|/SUDAM)? Nº "
        r"(\d+|xx|XX),"  # Permite número ou "xx" / "XX"
        r"\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+" # Permite dia ou "xx" / "XX"
        r"(\w+|xx|XX)\s+DE\s+(\d{4})" # Permite MÊS ou "xx" / "XX"
    )
    
    
    match = padrao_epigrafe.search(texto_completo)
    
    if not match:
        # Se o padrão estrito falhar, tentamos encontrar um padrão flexível
        # apenas para dar uma mensagem de erro mais útil para o usuário.
        padrao_flexivel = re.compile(r"MINUTA RESOLUÇÃO CONDEL.*? DE \d{4}", re.IGNORECASE)
        match_flexivel = padrao_flexivel.search(texto_completo)
        if match_flexivel:
            contexto = match_flexivel.group(0).strip()
            return {"status": "FALHA", "detalhe": [f"A epígrafe foi encontrada, mas sua formatação está incorreta. Verifique se está tudo em maiúsculas (exceto 'xx', se usado). Encontrado: '{contexto}'"]}
        else:
            return {"status": "FALHA", "detalhe": ["A linha da epígrafe não foi encontrada ou está fora do padrão 'RESOLUÇÃO CONDEL Nº..., DE...DE...DE...'."]}

    # Desempacota os 4 grupos: número, dia, mês, ano
    numero_res, dia_str, mes_str, ano_str = match.groups()[1:]
    
    # Se o mês for 'xx' (minúsculo ou maiúsculo), pulamos a validação de data e de maiúsculas.
    if mes_str.lower() == 'xx':
        pass 
    
    # Se o mês não for 'xx', ele deve ser MAIÚSCULO e uma data válida.
    else:
        # Regra 1: Verificar se o mês está em maiúsculas
        if not mes_str.isupper():
            erros.append(f"O mês na data da epígrafe deve estar em MAIÚSCULO. Foi encontrado: '{mes_str}'.")

        # Regra 2: Verificação de validade da data (só tentamos se o dia também não for 'xx')
        if dia_str.lower() != 'xx':
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
                data_str = f"{dia_str} de {mes_str.lower()} de {ano_str}"
                datetime.strptime(data_str, "%d de %B de %Y")
            except ValueError:
                erros.append(f"A data '{dia_str} de {mes_str} de {ano_str}' parece ser inválida (ex: dia 31 de abril).")
            except locale.Error:
                erros.append("Aviso: Não foi possível validar a data (locale 'pt_BR.UTF-8' não encontrado). Verificação de data pulada.")

    # Retorno
    if not erros:
        return {"status": "OK", "detalhe": "O formato da epígrafe e a data estão corretos."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_ementa(texto_completo):
    """Verifica se a ementa começa com um verbo de ação aceitável."""

    VERBOS_ACEITOS = [
        "Aprova", 
        "Altera", 
        "Dispõe", 
        "Regulamenta", 
        "Define",
        "Estabelece",
        "Autoriza",
        "Prorroga",
        "Revoga",
        "Atualização"
    ]

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
        []
        if not texto_ementa:
            return {"status": "FALHA", "detalhe": ["Não foi possível encontrar o texto da ementa após a data."]}
        
        primeira_palavra = texto_ementa.split()[0]
        
        if primeira_palavra in VERBOS_ACEITOS:
            return {"status": "OK", "detalhe": f"A ementa inicia corretamente com o verbo '{primeira_palavra}'."}
        else:
            return {"status": "FALHA", "detalhe": [f"A ementa deve começar com um verbo de ação (ex: Aprova, Altera), mas começou com '{primeira_palavra}'."]}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["A ementa parece estar vazia ou com formatação inválida."]}