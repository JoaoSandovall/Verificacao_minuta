import re

# --- COMPILAÇÃO GLOBAL DE EXPRESSÕES REGULARES ---
REGEX_EMENTA_IGNORAR = re.compile(r'^(MINISTÉRIO|SUPERINTENDÊNCIA|CONSELHO|MINUTA|RESOLUÇÃO|PORTARIA|DECRETO|ATO)', re.IGNORECASE)
REGEX_EMENTA_PARADA = re.compile(r'^(O PRESIDENTE|A DIRETORIA|Art\.|Artigo)', re.IGNORECASE)
REGEX_FECHO_PREAMBULO = re.compile(r"(?:o\s+colegiado\s+)?resolveu?\s*:", re.IGNORECASE)
REGEX_VERBO_ART1 = re.compile(r'^\s*Art\.\s*1[º°ᵒ\.]\s+([A-Za-zÇçÁ-Úá-ú]+)', re.MULTILINE)
REGEX_ANEXO_ASSINATURA = re.compile(r'\n\s*ANEXO', re.IGNORECASE)

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
    linhas = texto.split('\n')
    
    match_ementa = None
    
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        if not linha_limpa: continue

        if REGEX_EMENTA_IGNORAR.match(linha_limpa):
            continue
        
        letras = [c for c in linha_limpa if c.isalpha()]
        if letras and all(c.isupper() for c in letras):
            continue

        if REGEX_EMENTA_PARADA.match(linha_limpa):
            break

        match_regex = re.search(re.escape(linha_limpa), texto)
        if match_regex:
            match_ementa = match_regex
            break
    
    if not match_ementa:
        return {"status": "ALERTA", "detalhe": "Ementa não localizada."}
    
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
    
    match_fecho = REGEX_FECHO_PREAMBULO.search(texto_completo)
    
    erros = []
    
    if match_fecho:
        texto_encontrado = match_fecho.group(0)
        
        if texto_encontrado != "o Colegiado resolve:":
            erros.append({
                "mensagem": "O fecho do preâmbulo deve ser exatamente 'o Colegiado resolve:'.",
                "original": texto_encontrado,
                "sugestao": "o Colegiado resolve:",
                "span": match_fecho.span(),
                "tipo": "fixable"
            })
            
    else:
        erros.append({
            "mensagem": "Fecho 'o Colegiado resolve:' não encontrado no final do preâmbulo.", 
            "original": texto_completo[:50], 
            "tipo": "alert"
        })
        
    return erros

def auditar_verbo_primeiro_artigo(texto_completo):
    match = REGEX_VERBO_ART1.search(texto_completo)
    
    if not match:
        return {"status": "OK", "detalhe": "Art. 1º não localizado para análise de verbo."}
    
    palavra_encontrada = match.group(1)
    span_palavra = match.span(1)
    
    correcoes = {
        "Aprovar": "Aprova",
        "Alterar": "Altera",
    }

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
   
    match_anexo = REGEX_ANEXO_ASSINATURA.search(texto_completo)
    
    texto = texto_completo[:match_anexo.start()] if match_anexo else texto_completo
    
    linhas = [l.strip() for l in texto.strip().split('\n') if l.strip()]
    
    if linhas:
        ultimas = linhas[-3:]
        if not any(l.isupper() and len(l) > 5 and " " in l and not l.startswith("Art") for l in ultimas):
             return {"status": "FALHA", "detalhe": ["Bloco de assinatura não encontrado (Nome Maiúsculo)."]}
    return {"status": "OK", "detalhe": "Assinatura correta."}