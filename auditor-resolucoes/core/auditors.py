# core/auditors.py

import re
import locale
from datetime import datetime

# ----------------------------------------------------------------------
# R001: Verificação do Cabeçalho do Ministério
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# R002: Verificação da Epígrafe (Formato e Data)
# ----------------------------------------------------------------------
def auditar_epigrafe(texto_completo):
    """Verifica se a epígrafe (RESOLUÇÃO Nº..., DE...) está no formato correto."""
    erros = []
    
    # Tenta encontrar a linha da epígrafe no texto
    padrao_epigrafe = re.compile(r"RESOLUÇÃO Nº (\d+), DE (\d{1,2}) DE (\w+) DE (\d{4})", re.IGNORECASE)
    match = padrao_epigrafe.search(texto_completo)

    if not match:
        return {"status": "FALHA", "detalhe": ["ERRO R002: Linha da epígrafe não encontrada ou fora do padrão 'RESOLUÇÃO Nº ..., DE ...'."]}

    # Extrai as partes da data
    numero_res, dia_str, mes_str, ano_str = match.groups()
    
    # 1. Verifica se o mês está em minúsculo
    if not mes_str.islower():
        erros.append(f"ERRO R002A: O mês '{mes_str}' deve estar em minúsculo (ex: 'setembro').")
        
    # 2. Verifica se a data é válida (ex: não é 30 de fevereiro)
    try:
        # Configura o Python para entender nomes de meses em português
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        data_str = f"{dia_str} de {mes_str.lower()} de {ano_str}"
        # Tenta converter o texto em um objeto de data real
        datetime.strptime(data_str, "%d de %B de %Y")
    except ValueError:
        erros.append(f"ERRO R002B: A data '{dia_str} de {mes_str} de {ano_str}' é inválida.")
    except locale.Error:
        # Se o locale 'pt_BR.UTF-8' não estiver instalado no sistema, ignora o erro de data.
        # Isso garante que o código rode em qualquer máquina.
        pass

    if not erros:
        return {"status": "OK", "detalhe": "Formato da epígrafe e data estão corretos (R002)."}
    else:
        return {"status": "FALHA", "detalhe": erros}

# ----------------------------------------------------------------------
# R005: Verificação de Numeração de Artigos (Ordinal/Cardinal)
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# R008: Verificação de Pontuação de Incisos (VERSÃO FINAL CORRIGIDA)
# ----------------------------------------------------------------------
def auditar_pontuacao_incisos(texto_completo):
    """Verifica a pontuação de Incisos (I, II, ...), se eles existirem."""
    erros = []
    
    # Regex PRECISA: Encontra blocos que começam em uma nova linha com um 
    # numeral romano e um travessão. Isso evita confundir com outras palavras.
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

# ----------------------------------------------------------------------
# R010: Verificação de Uso de Siglas (Travessão vs. Parênteses)
# ----------------------------------------------------------------------
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
    
# Adicionar ao final de core/auditors.py

# ----------------------------------------------------------------------
# R003: Verificação da Ementa (Verbo Inicial)
# ----------------------------------------------------------------------
def auditar_ementa(texto_completo):
    """Verifica se a ementa começa com um verbo de ação aceitável."""
    
    # Lista de verbos comuns que iniciam uma ementa
    VERBOS_ACEITOS = [
        'Aprova', 'Altera', 'Dispõe', 'Regulamenta', 'Estabelece', 
        'Fixa', 'Define', 'Cria', 'Extingue', 'Revoga', 'Prorroga'
    ]
    
    # A ementa geralmente é o primeiro parágrafo após a linha da epígrafe (a data)
    try:
        # Encontra a linha da epígrafe para saber onde a ementa começa
        padrao_epigrafe = re.compile(r".* DE \d{4}", re.IGNORECASE)
        match_epigrafe = padrao_epigrafe.search(texto_completo)
        
        if not match_epigrafe:
            return {"status": "FALHA", "detalhe": ["ERRO R003: Não foi possível localizar a epígrafe para encontrar a ementa."]}
        
        # Pega todo o texto APÓS a epígrafe
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():]
        
        # O primeiro parágrafo não vazio é a ementa
        linhas_ementa = texto_apos_epigrafe.strip().split('\n')
        texto_ementa = ""
        for linha in linhas_ementa:
            if linha.strip(): # Pega a primeira linha que não está em branco
                texto_ementa = linha.strip()
                break
        
        if not texto_ementa:
             return {"status": "FALHA", "detalhe": ["ERRO R003: Não foi possível encontrar o texto da ementa."]}

        # Pega a primeira palavra da ementa
        primeira_palavra = texto_ementa.split()[0]
        
        # Verifica se a primeira palavra está na nossa lista de verbos
        if primeira_palavra in VERBOS_ACEITOS:
            return {"status": "OK", "detalhe": f"Ementa inicia corretamente com o verbo '{primeira_palavra}' (R003)."}
        else:
            return {"status": "FALHA", "detalhe": [f"ERRO R003: A ementa deve começar com um verbo de ação (ex: Aprova, Dispõe). Começou com '{primeira_palavra}'."]}

    except IndexError:
        return {"status": "FALHA", "detalhe": ["ERRO R003: A ementa parece estar vazia ou mal formatada."]}
    
def auditar_assinatura(texto_completo):
    linhas = [linha.strip() for linha in texto_completo.strip().split('\n') if linha.strip()]
    if len(linhas) < 2:
        return {"status": "FALHA", "detalhe": ["ERRO R012: Não foi possível encontrar um bloco de assinatura no final do documento."]}
    
    ultimas_linhas = linhas[-4:]
    
    try:
        indice_nome = -1
        for i, linha in enumerate(ultimas_linhas):
            
            if linha.isupper() and len(linha.split()) > 1:
                indice_nome = i
                break
        if indice_nome == -1:
            return {"status": "FALHA", "detalhe": ["ERRO R012: Nome do signatário em letras maiúsculas não encontrado no final do documento."]}
        
        linha_nome = ultimas_linhas[indice_nome]
        linha_cargo = ultimas_linhas[indice_nome + 1]
        
        if not linha_cargo or linha_cargo.isupper():
             return {"status": "FALHA", "detalhe": [f"ERRO R012: Cargo abaixo do nome '{linha_nome}' não encontrado ou está incorretamente em maiúsculas."]}
        
        return {"status": "OK", "detalhe": "Bloco de assinatura parece estar no formato correto (R012)."}
    

    except IndexError:
        return {"status": "FALHA", "detalhe": ["ERRO R012: Estrutura do bloco de assinatura inválida (nome sem cargo abaixo)."]}
    
def auditar_considerando(texto_completo):
    
    match = re.search(r'\n\s*CONSIDERANDO', texto_completo)
    
    if match:
        return {"status": "OK", "detalhe": "Seção 'CONSIDERANDO' encontrada e formatada corretamente (R004)."}
    else:
        # Faz uma segunda verificação 'case-insensitive' para dar um erro mais útil
        match_case_insensitive = re.search(r'\n\s*considerando', texto_completo, re.IGNORECASE)
        if match_case_insensitive:
            return {"status": "FALHA", "detalhe": ["ERRO R004: A palavra 'Considerando' foi encontrada, mas deve estar em letras maiúsculas ('CONSIDERANDO')."]}
        else:
            return {"status": "FALHA", "detalhe": ["ERRO R004: A seção obrigatória 'CONSIDERANDO' não foi encontrada no documento."]}