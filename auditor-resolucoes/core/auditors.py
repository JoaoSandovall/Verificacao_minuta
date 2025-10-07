# core/auditors.py

import re

# ----------------------------------------------------------------------
# R001: Verificação do Cabeçalho do Ministério
# Regra: O nome do Ministério deve estar em caixa alta, sem ponto final.
# ----------------------------------------------------------------------
def auditar_cabecalho_ministerio(texto_completo):
    """Verifica se o nome do ministério está no formato correto no início do documento."""
    
    padrao_correto = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    
    # Pega as primeiras linhas do texto para análise
    primeiras_linhas = texto_completo.strip().split('\n')
    
    if not primeiras_linhas:
        return {"status": "FALHA", "detalhe": ["ERRO R001: Documento vazio ou sem conteúdo."]}

    # A primeira linha não vazia deve ser o nome do ministério
    primeira_linha_conteudo = primeiras_linhas[0].strip()
    
    if primeira_linha_conteudo == padrao_correto:
        return {"status": "OK", "detalhe": "Cabeçalho do Ministério está correto (R001)."}
    else:
        detalhe_erro = f"ERRO R001: O cabeçalho do Ministério está incorreto. Esperado: '{padrao_correto}'. Encontrado: '{primeira_linha_conteudo}'."
        return {"status": "FALHA", "detalhe": [detalhe_erro]}

# ----------------------------------------------------------------------
# R005: Verificação de Numeração de Artigos (Ordinal/Cardinal)
# Regra: Art. 1º a 9º (Ordinal com º); Art. 10 em diante (Cardinal sem º).
# ----------------------------------------------------------------------
def auditar_numeracao_artigos(texto_completo):
    """Verifica se artigos 1º a 9º usam ordinal (º) e se 10 em diante usam cardinal (sem º)."""
    erros = []
    
    # Padrão A: Artigos de 1 a 9 que NÃO usam 'º' (ERRO)
    padrao_A = r'(Art\. [1-9])(?![º\s])' 
    for match in re.finditer(padrao_A, texto_completo):
        erros.append(f"ERRO R005A: '{match.group(1)}' - Artigo de 1 a 9 deve usar o indicador ordinal 'º' (ex: Art. 1º).")

    # Padrão B: Artigos de 10 em diante que usam 'º' (ERRO)
    padrao_B = r'(Art\. \d{2,})º' 
    for match in re.finditer(padrao_B, texto_completo):
        erros.append(f"ERRO R005B: '{match.group(1)}º' - Artigo a partir do 10 deve ser cardinal (sem 'º', ex: Art. 10).")

    if not erros:
        return {"status": "OK", "detalhe": "Numeração ordinal/cardinal dos artigos está correta (R005)."}
    else:
        return {"status": "FALHA", "detalhe": erros}


# ----------------------------------------------------------------------
# R008: Verificação de Pontuação de Incisos
# Regra: Incisos terminam com ; ou : (se tiver alíneas) ou . (se for o último).
# ----------------------------------------------------------------------
def auditar_pontuacao_incisos(texto_completo):
    """Verifica se a pontuação dos Incisos (I, II, III, IV, ...) está correta."""
    erros = []

    # Regex para encontrar Incisos (numerais romanos) e seu conteúdo até o próximo Inciso ou fim
    incisos = re.findall(r'[IVXLCDM]+\s*–?\s*.*?(?=[IVXLCDM]+\s*–?\s*|\Z)', texto_completo, re.DOTALL)
    
    # Filtra Incisos vazios ou muito curtos.
    incisos = [i.strip() for i in incisos if len(i.strip()) > 5]

    if not incisos:
        # Pode ser que a minuta não tenha incisos, o que não é um erro.
        return {"status": "OK", "detalhe": "Nenhum inciso encontrado para auditoria (R008)."}
        
    num_incisos = len(incisos)
    
    for i, inciso in enumerate(incisos):
        e_ultimo = (i == num_incisos - 1)
        # Verifica se o inciso contém alíneas (padrão de a) b) c) )
        termina_com_alínea = re.search(r'\n\s*[a-z]\)', inciso)
        
        # Pega o último caractere do inciso (limpa espaços/quebras de linha antes)
        terminacao_atual = inciso.rstrip().strip()[-1] 
        
        # O último deve terminar com PONTO.
        if e_ultimo:
            if terminacao_atual != '.':
                erros.append(f"ERRO R008C: Último inciso da sequência (Inciso {i+1}) deve terminar com PONTO (.). Terminação atual: '{terminacao_atual}'")
        
        # Os intermediários: PONTO E VÍRGULA, a menos que tenha alíneas (:).
        else: 
            if termina_com_alínea and terminacao_atual != ':':
                 erros.append(f"ERRO R008B: Inciso {i+1} tem alíneas, mas não termina com DOIS PONTOS (:). Terminação atual: '{terminacao_atual}'")
            elif not termina_com_alínea and terminacao_atual != ';':
                 erros.append(f"ERRO R008A: Inciso {i+1} deve terminar com PONTO E VÍRGULA (;). Terminação atual: '{terminacao_atual}'")

    if not erros:
        return {"status": "OK", "detalhe": "Pontuação dos incisos está conforme a regra (R008)."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_uso_siglas(texto_completo):
    """Verifica se as siglas estão usando travessão ou se estão incorretamente em parênteses ou sem separação."""
    erros = []

    # 1. Procurar por Siglas entre parênteses (ERRO)
    padrao_parenteses = r'\([A-Z]{2,}\)'
    for match in re.finditer(padrao_parenteses, texto_completo):
        erros.append(f"ERRO R010A: Sigla entre parênteses encontrada: '{match.group(0)}'. Use travessão (–) em seu lugar.")

    # 2. Procurar por Siglas sem separação (Ex: Centro-Oeste FDCO) (ERRO)
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("ERRO R010B: 'Centro-Oeste FDCO' - A sigla não está separada por travessão. O correto seria 'Centro-Oeste – FDCO'.")

    if not erros:
        return {"status": "OK", "detalhe": "Uso de siglas está conforme a regra (R010)."}
    else:
        return {"status": "FALHA", "detalhe": erros}