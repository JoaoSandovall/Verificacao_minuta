import re

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
    """
    Verifica a numeração e o espaçamento dos artigos com regras mais rígidas.
    - Art. 1º a 9º: Deve ser 'Art. N°  ' (com º e dois espaços).
    - Art. 10 em diante: Deve ser 'Art. NN.  ' (com . e dois espaços).
    """
    erros = []
    
    # Encontra todas as ocorrências de "Art. [número]" para análise individual
    matches = re.finditer(r'Art\.\s*(\d+)', texto_completo)

    for match in matches:
        numero_artigo_str = match.group(1)
        numero_artigo = int(numero_artigo_str)
        
        # Pega a fatia do texto original logo após o match para verificar pontuação e espaços
        pos_fim_match = match.end()
        trecho_apos_artigo = texto_completo[pos_fim_match : pos_fim_match + 3]

        # --- VALIDAÇÃO PARA ARTIGOS DE 1 A 9 ---
        if 1 <= numero_artigo <= 9:
            padrao_esperado = "º  "
    
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
                if trecho_apos_artigo.startswith('°'):
                    erros.append(f"No 'Art. {numero_artigo}', o símbolo ordinal está incorreto. Use 'º' em vez de '°'.")
                elif not trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido pelo ordinal 'º'.")
                elif not trecho_apos_artigo.startswith('º  '):
                    erros.append(f"Após 'Art. {numero_artigo}º', deve haver exatamente dois espaços.")
                else:
                     erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: 'º' seguido de dois espaços.")

        # --- VALIDAÇÃO PARA ARTIGOS 10 EM DIANTE ---
        elif numero_artigo >= 10:
            padrao_esperado = ".  "
            
            if not trecho_apos_artigo.startswith(padrao_esperado):
                # Análise do erro específico
                if trecho_apos_artigo.startswith('º'):
                    erros.append(f"O 'Art. {numero_artigo}' não deve usar o ordinal 'º', mas sim um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.'):
                    erros.append(f"O 'Art. {numero_artigo}' deve ser seguido por um ponto final (.).")
                elif not trecho_apos_artigo.startswith('.  '):
                     erros.append(f"Após 'Art. {numero_artigo}.', deve haver exatamente dois espaços.")
                else: # Outros erros de formatação
                    erros.append(f"A formatação após 'Art. {numero_artigo}' está incorreta. Esperado: '.' seguido de dois espaços.")

    if not erros:
        return {"status": "OK", "detalhe": "A numeração e espaçamento dos artigos estão corretos."}
    else:
        # Usa list(set(erros)) para remover mensagens de erro duplicadas
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}
    
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
    
# Adicione esta nova função ao final do arquivo core/regras/regras_corpo.py

def auditar_pontuacao_alineas(texto_completo):
    """Verifica a pontuação das Alíneas (a, b, c...), se elas existirem."""
    erros = []
    
    # Encontra todos os blocos de alíneas no texto
    # (procura por múltiplas linhas que começam com 'letra)')
    blocos_alineas = re.finditer(r'((?:\n\s*[a-z]\).*?)+)', texto_completo)
    
    for bloco in blocos_alineas:
        # Pega todas as alíneas dentro de um bloco
        alineas = re.findall(r'(\n\s*[a-z]\).*)', bloco.group(1))
        
        if len(alineas) < 2:
            continue

        num_alineas = len(alineas)
        for i, alinea in enumerate(alineas):
            alinea_limpa = alinea.strip()
            e_ultima = (i == num_alineas - 1)
            
            # Regra 1: A última alínea deve terminar com ponto final.
            if e_ultima:
                if not alinea_limpa.endswith('.'):
                    erros.append(f"A última alínea do bloco ('{alinea_limpa[:30]}...') deve terminar com ponto final (.).")
            # Regra 2: As alíneas intermediárias devem terminar com ponto e vírgula.
            else:
                if not alinea_limpa.endswith(';'):
                    erros.append(f"A alínea intermediária ('{alinea_limpa[:30]}...') deve terminar com ponto e vírgula (;).")

    if not erros:
        return {"status": "OK", "detalhe": "A pontuação das alíneas (a, b, c...) está correta."}
    else:
        # Retorna apenas os 3 primeiros erros para não poluir a interface
        return {"status": "FALHA", "detalhe": erros[:3]}