# core/regras/regras_cabecalho.py
import re
import locale
from datetime import datetime

def auditar_cabecalho_ministerio(texto_completo):
    """Verifica se o nome do ministério está no formato correto no início do documento."""
    padrao_correto = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    if not primeiras_linhas:
        return {"status": "FALHA", "detalhe": ["ERRO R001: Documento vazio ou sem conteúdo."]}
    primeira_linha_conteudo = primeiras_linhas[0].strip()
    if primeira_linha_conteudo == padrao_correto:
        return {"status": "OK", "detalhe": "Cabeçalho do Ministério está correto (R001)."}
    else:
        detalhe_erro = f"ERRO R001: O cabeçalho do Ministério está incorreto. Esperado: '{padrao_correto}'. Encontrado: '{primeira_linha_conteudo}'."
        return {"status": "FALHA", "detalhe": [detalhe_erro]}

def auditar_epigrafe(texto_completo):
    """Verifica se a epígrafe (RESOLUÇÃO Nº..., DE...) está no formato correto."""
    erros = []
    padrao_epigrafe = re.compile(r"RESOLUÇÃO Nº (\d+), DE (\d{1,2}) DE (\w+) DE (\d{4})", re.IGNORECASE)
    match = padrao_epigrafe.search(texto_completo)
    if not match:
        return {"status": "FALHA", "detalhe": ["ERRO R002: Linha da epígrafe não encontrada ou fora do padrão 'RESOLUÇÃO Nº ..., DE ...'."]}
    numero_res, dia_str, mes_str, ano_str = match.groups()
    if not mes_str.islower():
        erros.append(f"ERRO R002A: O mês '{mes_str}' deve estar em minúsculo (ex: 'setembro').")
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        data_str = f"{dia_str} de {mes_str.lower()} de {ano_str}"
        datetime.strptime(data_str, "%d de %B de %Y")
    except ValueError:
        erros.append(f"ERRO R002B: A data '{dia_str} de {mes_str} de {ano_str}' é inválida.")
    except locale.Error:
        pass
    if not erros:
        return {"status": "OK", "detalhe": "Formato da epígrafe e data estão corretos (R002)."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_ementa(texto_completo):
    """Verifica se a ementa começa com um verbo de ação aceitável."""
    VERBOS_ACEITOS = ['Aprova', 'Altera', 'Dispõe', 'Regulamenta', 'Estabelece', 'Fixa', 'Define', 'Cria', 'Extingue', 'Revoga', 'Prorroga']
    try:
        padrao_epigrafe = re.compile(r".* DE \d{4}", re.IGNORECASE)
        match_epigrafe = padrao_epigrafe.search(texto_completo)
        if not match_epigrafe:
            return {"status": "FALHA", "detalhe": ["ERRO R003: Não foi possível localizar la epígrafe para encontrar a ementa."]}
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():]
        linhas_ementa = texto_apos_epigrafe.strip().split('\n')
        texto_ementa = ""
        for linha in linhas_ementa:
            if linha.strip():
                texto_ementa = linha.strip()
                break
        if not texto_ementa:
            return {"status": "FALHA", "detalhe": ["ERRO R003: Não foi possível encontrar o texto da ementa."]}
        primeira_palavra = texto_ementa.split()[0]
        if primeira_palavra in VERBOS_ACEITOS:
            return {"status": "OK", "detalhe": f"Ementa inicia corretamente com o verbo '{primeira_palavra}' (R003)."}
        else:
            return {"status": "FALHA", "detalhe": [f"ERRO R003: A ementa deve começar com um verbo de ação (ex: Aprova, Dispõe). Começou com '{primeira_palavra}'."]}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["ERRO R003: A ementa parece estar vazia ou mal formatada."]}