import re
from core.utils import _roman_to_int

def auditar_anexo(texto_completo):
    """Verifica se a seção 'ANEXO' existe e formatação."""
    match_correto = re.search(r'\n\s*(ANEXO)\s*(?=\n|$)', texto_completo)
    if match_correto:
         return {"status": "OK", "detalhe": "Seção 'ANEXO' encontrada e formatada corretamente."}

    match_incorreto = re.search(r'\n\s*(ANEXO\b.*?)\s*(?=\n|$)', texto_completo, re.IGNORECASE)
    if match_incorreto:
        palavra_encontrada = match_incorreto.group(1).strip()
        return {"status": "FALHA", "detalhe": [f"Formato de 'Anexo' incorreto. Encontrado: '{palavra_encontrada}'. Esperado: 'ANEXO' (exatamente, em maiúsculas e sozinho na linha)."]}
    
    return {"status": "OK", "detalhe": "Aviso: Nenhuma seção 'ANEXO' foi encontrada (Não obrigatório)."}

def auditar_sequencia_capitulos_anexo(texto_completo):
    """(Anexo) Verifica a sequência dos Capítulos (I, II, III...)."""
    erros = []
    matches = re.finditer(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    capitulos = [match.group(1) for match in matches]
    
    if not capitulos:
        return {"status": "OK", "detalhe": "Nenhum Capítulo encontrado para análise."}

    expected_numeral = 1
    for i, numeral_romano in enumerate(capitulos):
        current_numeral = _roman_to_int(numeral_romano)
        
        if current_numeral != expected_numeral:
            erro = f"Sequência de Capítulos incorreta. Esperado Capítulo de valor {expected_numeral} (Romano), mas encontrado '{numeral_romano}'."
            erros.append(erro)
            expected_numeral = current_numeral # Re-sincroniza
        
        expected_numeral += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Capítulos está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_secoes_anexo(texto_completo):
    """(Anexo) Verifica a sequência das Seções (I, II, III...) dentro de cada Capítulo."""
    erros = []
    # Divide o texto por Capítulos para analisar as seções de cada um
    blocos_capitulo = re.split(r'^\s*CAPÍTULO\s+[IVXLCDM]+', texto_completo, flags=re.MULTILINE)
    
    capitulos_encontrados = re.findall(r'^\s*CAPÍTULO\s+([IVXLCDM]+)', texto_completo, re.MULTILINE)
    
    # O primeiro bloco é o texto *antes* do CAPÍTULO I, então pulamos
    for i, bloco_texto in enumerate(blocos_capitulo[1:]):
        # Pega o nome do capítulo atual para usar na msg de erro
        nome_capitulo = capitulos_encontrados[i] if i < len(capitulos_encontrados) else 'desconhecido'
        
        matches = re.finditer(r'^\s*Seção\s+([IVXLCDM]+)', bloco_texto, re.MULTILINE)
        secoes = [match.group(1) for match in matches]
        
        if not secoes:
            continue # Capítulo pode não ter seções, o que é OK

        expected_numeral = 1
        for numeral_romano in secoes:
            current_numeral = _roman_to_int(numeral_romano)
            
            if current_numeral != expected_numeral:
                erro = f"Sequência de Seções incorreta dentro do CAPÍTULO {nome_capitulo}. Esperado Seção de valor {expected_numeral} (Romano), mas encontrado '{numeral_romano}'."
                erros.append(erro)
                expected_numeral = current_numeral # Re-sincroniza
            
            expected_numeral += 1
            
    if not erros:
        return {"status": "OK", "detalhe": "A sequência das Seções (reiniciando por Capítulo) está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_sequencia_artigos_anexo(texto_completo):
    """(Anexo) Verifica se a sequência de Artigos (1, 2, 3...) está correta (contínua)."""
    erros = []
    matches = re.finditer(r'Art\.\s*(\d+)', texto_completo)
    artigos = [int(match.group(1)) for match in matches]
    
    if not artigos:
        return {"status": "OK", "detalhe": "Nenhum Artigo encontrado no Anexo para análise de sequência."}

    # No Anexo do exemplo, a contagem é contínua e começa em 1.
    expected_num = 1
    if artigos[0] != 1:
        erros.append(f"O primeiro Artigo do Anexo não é 'Art. 1º'. Encontrado: 'Art. {artigos[0]}'.")
        expected_num = artigos[0]

    for num in artigos:
        if num != expected_num:
            erros.append(f"Sequência de Artigos incorreta no Anexo. Esperado 'Art. {expected_num}', mas encontrado 'Art. {num}'.")
            expected_num = num # Re-sincroniza
        expected_num += 1

    if not erros:
        return {"status": "OK", "detalhe": "A sequência dos Artigos no Anexo está correta."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_hierarquica_anexo(texto_completo):
    """
    (NOVA REGRA - Anexo) Verifica a pontuação hierárquica (Regras A, B, C)
    de Artigos, Parágrafos, Incisos e Alíneas.
    """
    erros = []
    
    padrao_itens = re.compile(
        r"^(?:[ \t]*)((Art\.\s*\d+[º°\.]?|Parágrafo\s+único\.?|§\s*\d+[º°\.]?)|([IVXLCDM]+[\s\-–])|([a-z]\)))(.*)", 
        re.MULTILINE | re.IGNORECASE
    )
    
    matches = list(re.finditer(padrao_itens, texto_completo))
    
    for i, match in enumerate(matches):
        linha_completa = match.group(0).strip()
        marcador_item = match.group(1).strip()
        
        # Ignora linhas de CAPÍTULO ou Seção (que podem ser pegas por 'I -')
        if re.match(r'^CAPÍTULO', linha_completa, re.I) or re.match(r'^Seção', linha_completa, re.I):
            continue
            
        # Determina o tipo do item atual
        tipo_atual = None
        if re.match(r'Art\.|Parágrafo|§', marcador_item, re.I):
            tipo_atual = "Artigo/Paragrafo"
        elif re.match(r'^[IVXLCDM]+', marcador_item):
            tipo_atual = "Inciso"
        elif re.match(r'^[a-z]\)', marcador_item):
            tipo_atual = "Alinea"

        # Pega o próximo item, se existir
        proximo_match = matches[i + 1] if (i + 1) < len(matches) else None
        
        # --- REGRA 1: ABERTURA (Dois-Pontos ':') ---
        inicia_subdivisao = False
        if proximo_match:
            marcador_proximo = proximo_match.group(1).strip()
            
            # Verifica se o próximo item é um Inciso
            proximo_eh_inciso = bool(re.match(r'^[IVXLCDM]+', marcador_proximo))
            # Verifica se o próximo item é uma Alínea
            proximo_eh_alinea = bool(re.match(r'^[a-z]\)', marcador_proximo))

            if tipo_atual == "Artigo/Paragrafo" and proximo_eh_inciso:
                inicia_subdivisao = True # Art/§ seguido por Inciso
            elif tipo_atual == "Inciso" and proximo_eh_alinea:
                inicia_subdivisao = True # Inciso seguido por Alínea
        
        if inicia_subdivisao:
            if not linha_completa.endswith(':'):
                erros.append(f"Pontuação de Abertura Incorreta: '{linha_completa}' deve terminar com ':' pois é seguido por uma subdivisão.")
            continue # Regra 1 verificada, pular para o próximo item
            
        # --- REGRAS 2 (Declaração) e 3 (Lista) ---
        
        # Itens do tipo Artigo/Parágrafo (Regra C: Declaração)
        if tipo_atual == "Artigo/Paragrafo":
            if not linha_completa.endswith('.'):
                erros.append(f"Pontuação de Declaração Incorreta: '{linha_completa}' deve terminar com '.'.")
            continue
            
        # Itens do tipo Inciso ou Alínea (Regra B: Lista)
        if tipo_atual in ("Inciso", "Alinea"):
            
            # Pega o tipo do próximo item
            tipo_proximo = None
            if proximo_match:
                marcador_proximo = proximo_match.group(1).strip()
                if re.match(r'Art\.|Parágrafo|§', marcador_proximo, re.I):
                    tipo_proximo = "Artigo/Paragrafo"
                elif re.match(r'^[IVXLCDM]+', marcador_proximo):
                    tipo_proximo = "Inciso"
                elif re.match(r'^[a-z]\)', marcador_proximo):
                    tipo_proximo = "Alinea"
            
            # Se o próximo item é do *mesmo* tipo (ex: Inciso I -> Inciso II)
            # OU se é uma Alínea seguida por um Inciso (ex: b) -> VIII -)
            if (proximo_match and tipo_proximo == tipo_atual) or \
               (tipo_atual == "Alinea" and tipo_proximo == "Inciso"):
                
                # É um item intermediário OU penúltimo.
                # Deve terminar com ';', '; e', ou '; ou'.
                if not (linha_completa.endswith(';') or linha_completa.endswith('; e') or linha_completa.endswith('; ou')):
                    erros.append(f"Pontuação de Lista Incorreta: '{linha_completa}' deve terminar com ';', '; e', ou '; ou'.")

            # Se é o último item da lista (não há próximo item, ou o próximo é de tipo MAIOR, como Artigo/Parágrafo)
            else:
                # É o item final da lista. Deve terminar com '.'
                if not linha_completa.endswith('.'):
                    erros.append(f"Pontuação de Fim de Lista Incorreta: '{linha_completa}' deveria terminar com '.' (ponto final), pois é o último item do seu bloco.")

    if not erros:
        return {"status": "OK", "detalhe": "A pontuação hierárquica do Anexo está correta."}
    else:
        return {"status": "FALHA", "detalhe": list(set(erros))[:5]}