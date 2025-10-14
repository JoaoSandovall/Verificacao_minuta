import re

# Substitua a função auditar_preambulo antiga por esta versão simplificada:

def auditar_preambulo(texto_completo):
    """
    Verifica a formatação do Preâmbulo, focando na autoridade ('O PRESIDENTE...')
    e na terminação com 'RESOLVE:'.
    """
    erros = []

    # Passo 1: Isolar o texto do preâmbulo (entre a ementa e o Art. 1º)
    try:
        match_epigrafe = re.search(r".* DE \d{4}", texto_completo, re.IGNORECASE)
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():].strip()
        linhas_ementa = texto_apos_epigrafe.strip().split('\n')
        pos_fim_ementa = texto_apos_epigrafe.find(linhas_ementa[0]) + len(linhas_ementa[0])
        
        match_artigo1 = re.search(r'Art\.\s*1[ºo]', texto_completo, re.IGNORECASE)
        
        texto_preambulo = texto_completo[match_epigrafe.end() + pos_fim_ementa : match_artigo1.start()].strip()
    except (AttributeError, IndexError):
        return {"status": "FALHA", "detalhe": ["Não foi possível isolar o texto do preâmbulo para análise."]}

    if not texto_preambulo:
        return {"status": "FALHA", "detalhe": ["O texto do preâmbulo parece estar vazio."]}

    # Passo 2: Verificar apenas as duas regras solicitadas

    # Regra 1: Título da autoridade em maiúsculas
    padrao_autoridade = r"O PRESIDENTE DO CONSELHO DELIBERATIVO"
    if not re.search(padrao_autoridade, texto_preambulo):
        if re.search(padrao_autoridade, texto_preambulo, re.IGNORECASE):
            erros.append("O título da autoridade (ex: 'O PRESIDENTE DO CONSELHO...') deve estar em maiúsculas.")
        else:
            erros.append("O título da autoridade (ex: 'O PRESIDENTE DO CONSELHO...') não foi encontrado no preâmbulo.")

    # Regra 2: A palavra 'RESOLVE:' no final, em maiúsculas
    if not texto_preambulo.endswith("RESOLVE:"):
        if texto_preambulo.lower().endswith("resolve:"):
            erros.append("A palavra 'RESOLVE:' no final do preâmbulo deve estar em maiúsculas.")
        else:
            erros.append("O preâmbulo deve terminar com a palavra 'RESOLVE:'.")
            
    # Passo 3: Retornar o resultado
    if not erros:
        return {"status": "OK", "detalhe": "O preâmbulo inicia com a autoridade e termina com 'RESOLVE:' corretamente."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_numeracao_artigos(texto_completo):
    """Verifica se artigos 1º a 9º usam ordinal (º) e se 10 em diante usam cardinal (sem º)."""
    erros = []
    # Procura por Art. 1-9 sem o 'º'
    padrao_A = r'(Art\. [1-9])(?![º\s])'
    for match in re.finditer(padrao_A, texto_completo):
        erros.append(f"O artigo '{match.group(1)}' deve usar o indicador ordinal 'º' (ex: Art. 1º, Art. 9º).")
    
    # Procura por Art. 10+ com o 'º'
    padrao_B = r'(Art\. \d{2,})º'
    for match in re.finditer(padrao_B, texto_completo):
        erros.append(f"O artigo '{match.group(1)}º' não deve usar o indicador ordinal 'º' (ex: Art. 10, Art. 25).")
        
    if not erros:
        return {"status": "OK", "detalhe": "A numeração dos artigos (ordinais e cardinais) está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_incisos(texto_completo):
    """Verifica a pontuação de Incisos (I, II, ...), se eles existirem."""
    erros = []
    incisos = re.findall(r'(^[ \t]*[IVXLCDM]+\s*–.*?(?=\n[ \t]*[IVXLCDM]+\s*–|\Z))', texto_completo, re.MULTILINE | re.DOTALL)
    if not incisos:
        return {"status": "OK", "detalhe": "Nenhum inciso (I-, II-, etc.) foi encontrado para análise."}
    
    num_incisos = len(incisos)
    for i, inciso_texto in enumerate(incisos):
        e_ultimo = (i == num_incisos - 1)
        terminacao_atual = inciso_texto.strip()[-1]
        numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_texto.strip()).group(1)
        tem_alineas = re.search(r':\s*\n\s*[a-z]\)', inciso_texto)
        
        if e_ultimo:
            if terminacao_atual != '.':
                erros.append(f"O último inciso (Inciso {numeral_romano}) deve terminar com ponto final (.).")
        else:
            if tem_alineas and terminacao_atual != ':':
                erros.append(f"O Inciso {numeral_romano} precede alíneas e deve terminar com dois-pontos (:).")
            elif not tem_alineas and terminacao_atual != ';':
                erros.append(f"O Inciso {numeral_romano} deve terminar com ponto e vírgula (;).")
                
    if not erros:
        return {"status": "OK", "detalhe": "A pontuação dos incisos está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_uso_siglas(texto_completo):
    """Verifica se as siglas estão usando travessão ou se estão incorretamente em parênteses ou sem separação."""
    erros = []
    # Procura por siglas entre parênteses, que é um erro
    padrao_parenteses = r'\([A-Z]{2,}\)'
    for match in re.finditer(padrao_parenteses, texto_completo):
        erros.append(f"A sigla '{match.group(0)}' não deve estar entre parênteses. Use um travessão (–).")
    
    # Procura por um caso específico comum de erro
    if "Centro-Oeste FDCO" in texto_completo:
        erros.append("A sigla 'FDCO' não está separada por travessão. O correto seria '...Centro-Oeste – FDCO'.")
        
    if not erros:
        return {"status": "OK", "detalhe": "A formatação das siglas está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}