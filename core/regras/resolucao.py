import re

def auditar_cabecalho(texto_completo):
    
    padrao_base = "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL"
    primeiras_linhas = texto_completo.strip().split('\n')
    
    if not primeiras_linhas: 
        return {"status": "FALHA", "detalhe": ["Documento vazio."]}
    
    linha1 = primeiras_linhas[0].strip()
    
    if padrao_base in linha1.upper():
        return {"status": "OK", "detalhe": "Cabeçalho CEG correto."}
    return {"status": "FALHA", "detalhe": [f"Cabeçalho deve ser '{padrao_base}'. Encontrado: '{linha1}'"]}

def auditar_epigrafe(texto_completo, regex_compilado, msgs_erro_personalizadas=None):
    
    if msgs_erro_personalizadas is None:
        msgs_erro_personalizadas = ["Padrão de epígrafe não encontrado."]
    
    match = regex_compilado.search(texto_completo)
    
    if not match:
        if "N°" in texto_completo or "Nº" in texto_completo:
             return {"status": "FALHA", "detalhe": ["Epígrafe usando símbolo errado. Use 'Nᵒ' (Ordinal)."]}
        return {"status": "FALHA", "detalhe": msgs_erro_personalizadas}
    
    texto_epigrafe = match.group(0)
    # Verifica maiúsculas ignorando 'Minuta de'
    
    texto_limpo = re.sub(r'[^A-Za-zÇçÁ-Úá-ú]', '', texto_epigrafe)
    
    if not texto_limpo.isupper():
        return {
            "status": "FALHA",
            "detalhe": {
                "mensagem": "A epígrafe deve estar totalmente em MAIÚSCULAS (Ex: RESOLUÇÃO).",
                "original": texto_epigrafe,
                "sugestao": texto_epigrafe.upper(),
                "span": match.span(),
                "tipo": "fixable"
            }
        }
    return {"status": "OK", "detalhe": "Epígrafe correta."}

def auditar_ementa(texto):
    """
    Localiza a Ementa lendo linha por linha, descartando o que não é.
    """
    linhas = texto.split('\n')
    
    match_ementa = None
    
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        if not linha_limpa: continue

        if re.match(r'^(MINISTÉRIO|SUPERINTENDÊNCIA|CONSELHO|MINUTA|RESOLUÇÃO|PORTARIA|DECRETO|ATO)', linha_limpa, re.IGNORECASE):
            continue
        
        letras = [c for c in linha_limpa if c.isalpha()]
        if letras and all(c.isupper() for c in letras):
            continue

        if re.match(r'^(O PRESIDENTE|A DIRETORIA|Art\.|Artigo)', linha_limpa, re.IGNORECASE):
            break

        match_regex = re.search(re.escape(linha_limpa), texto)
        if match_regex:
            match_ementa = match_regex
            break
    
    if not match_ementa:
        return {"status": "ALERTA", "detalhe": "Ementa não localizada."}

    # Validação do Verbo
    texto_ementa = match_ementa.group(0)
    span_ementa = match_ementa.span()
    primeira_palavra = texto_ementa.split(' ')[0]
    verbo_limpo = re.sub(r'[^\w]', '', primeira_palavra)
    verbos_aceitos = ["Aprova", "Institui", "Altera", "Dispõe", "Estabelece", "Cria", "Homologa", "Define", "Torna"]

    msg_erro = None

    if primeira_palavra[0].islower():
        msg_erro = f"Verbo da Ementa minúsculo ('{primeira_palavra}')."
    elif verbo_limpo not in verbos_aceitos:
        msg_erro = f"Início inválido ('{primeira_palavra}'). Esperado um verbo (ex: Aprova)."

    if msg_erro:
        return {
            "status": "FALHA",
            "detalhe": {
                "mensagem": msg_erro, 
                "original": texto_ementa,
                "span": span_ementa, 
                "tipo": "highlight"
            }
        }
    return {"status": "OK", "detalhe": "Ementa válida."}

def verificar_fecho_preambulo(texto_completo):
    # Procura por "resolve" ou "resolveu" seguido de dois pontos, ignorando maiúsculas na busca
    match_fecho = re.search(r"(resolveu?)\s*:", texto_completo, re.IGNORECASE)
    
    erros = []
    
    if match_fecho:
        verbo_encontrado = match_fecho.group(1) # Captura a palavra (ex: Resolve, resolveu, RESOLVEU)
        texto_completo_match = match_fecho.group(0) # Captura com os dois pontos (ex: resolveu:)
        
        if verbo_encontrado != "resolve":
            erros.append({
                "mensagem": "O fecho deve ser apenas 'resolve:' (em minúsculo).",
                "original": texto_completo_match,
                "span": match_fecho.span(),
                "tipo": "highlight"
            })
            
    else:
        erros.append({
            "mensagem": "Fecho 'resolve:' não encontrado no final do preâmbulo.", 
            "original": texto_completo[:50], 
            "tipo": "alert"
        })
        
    return erros

def auditar_verbo_primeiro_artigo(texto_completo):
    """
    Verifica se o Art. 1º começa com verbo no presente do indicativo (Aprova, Altera),
    e não no infinitivo (Aprovar, Alterar).
    """
    # Regex: Procura 'Art. 1' (com qualquer símbolo) e captura a primeira palavra depois dele
    match = re.search(r'^\s*Art\.\s*1[º°ᵒ\.]\s+([A-Za-zÇçÁ-Úá-ú]+)', texto_completo, re.MULTILINE)
    
    if not match:
        # Se não achou Art. 1º, deixa quieto (outra regra avisa que falta artigo)
        return {"status": "OK", "detalhe": "Art. 1º não localizado para análise de verbo."}
    
    palavra_encontrada = match.group(1)
    span_palavra = match.span(1)
    
    # Mapa de correções comuns (Infinitivo -> Presente)
    correcoes = {
        "Aprovar": "Aprova",
        "Alterar": "Altera",
    }
    
    # 1. Verifica se está na lista de erros comuns
    if palavra_encontrada in correcoes:
        sugestao = correcoes[palavra_encontrada]
        return {
            "status": "FALHA",
            "detalhe": {
                "mensagem": f"O Art. 1º deve começar com o verbo no presente ('{sugestao}'), evite o infinitivo.",
                "original": palavra_encontrada,
                "span": span_palavra,
                "tipo": "highlight"
            }
        }
        
    verbos_validos = list(correcoes.values()) + ["Fica", "Torna"]
    
    if palavra_encontrada not in verbos_validos:
        
        pass

    return {"status": "OK", "detalhe": "Verbo do Art. 1º correto."}

def auditar_fecho_vigencia(texto_completo):
    if "Esta Resolução entra em vigor" not in texto_completo:
         return {"status": "FALHA", "detalhe": ["Cláusula de vigência não encontrada."]}
    return {"status": "OK", "detalhe": "Vigência encontrada."}

def auditar_assinatura(texto_completo):
   
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    
    texto = texto_completo[:match_anexo.start()] if match_anexo else texto_completo
    
    linhas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
    
    if linhas:
        ultimas = linhas[-3:]
        if not any(l.isupper() and len(l) > 5 and " " in l and not l.startswith("Art") for l in ultimas):
             return {"status": "FALHA", "detalhe": ["Bloco de assinatura não encontrado (Nome Maiúsculo)."]}
    return {"status": "OK", "detalhe": "Assinatura correta."}