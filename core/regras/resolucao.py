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
        if not linha_limpa: continue # Pula vazias

        # 1. Pula Cabeçalhos/Epígrafes conhecidos
        if re.match(r'^(MINISTÉRIO|SUPERINTENDÊNCIA|CONSELHO|MINUTA|RESOLUÇÃO|PORTARIA|DECRETO|ATO)', linha_limpa, re.IGNORECASE):
            continue
        
        # 2. Pula linhas totalmente MAIÚSCULAS (provavelmente cabeçalhos extras)
        letras = [c for c in linha_limpa if c.isalpha()]
        if letras and all(c.isupper() for c in letras):
            continue

        # 3. Se chegou no Preâmbulo ou Artigo, paramos (Ementa não achada antes)
        if re.match(r'^(O PRESIDENTE|A DIRETORIA|Art\.|Artigo)', linha_limpa, re.IGNORECASE):
            break
            
        # 4. Se sobreviveu, É A EMENTA!
        # Precisamos achar a posição original no texto para o span
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
    
    match_fecho = re.search(r"(o\s+Colegiado\s+)?(resolveu?)\s*:", texto_completo, re.IGNORECASE)
    
    erros = []
    
    if match_fecho:
        tem_colegiado = bool(match_fecho.group(1))
        verbo = match_fecho.group(2).lower()
       
        if tem_colegiado and verbo == "resolve":
            erros.append({"mensagem": "Com 'Colegiado', use 'resolveu'.", "original": match_fecho.group(0), "sugestao": match_fecho.group(1)+"resolveu:", "span": match_fecho.span(), "tipo": "fixable"})
        elif not tem_colegiado and verbo == "resolveu":
            erros.append({"mensagem": "Sem 'Colegiado', use 'resolve'.", "original": match_fecho.group(0), "sugestao": "resolve:", "span": match_fecho.span(), "tipo": "fixable"})
    else:
        erros.append({"mensagem": "Fecho 'resolve:' não encontrado.", "original": texto_completo[:50], "tipo": "alert"})
    return erros

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