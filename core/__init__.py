from .regras import comuns, condel, ceg, anexo

def identificar_tipo_resolucao(texto):
    if not texto: 
        return "DESCONHECIDO"
    
    inicio = texto[:1000].upper()
    
    if "RESOLUÇÃO CEG" in inicio or "CEG/MIDR" in inicio:
        return "CEG"
    elif "RESOLUÇÃO CONDEL" in inicio or "CONDEL/SUDECO" in inicio:
        return "CONDEL"
    
    return "DESCONHECIDO"

def obter_regras(texto_completo):
    
    tipo = identificar_tipo_resolucao(texto_completo)
    
    # 1. Regras Comuns (Base)
    regras = {
        "Cabeçalho (MINISTÉRIO/CONSELHO)": comuns.auditar_cabecalho,
        "Ementa (Verbo Inicial)": comuns.auditar_ementa,
        "Bloco de Assinatura": comuns.auditar_assinatura,
        "Fecho de Vigência": comuns.auditar_fecho_vigencia,
        "Artigos (Formato Numeração)": comuns.auditar_numeracao_artigos,
        "Parágrafos (§ Espaçamento)": comuns.auditar_espacamento_paragrafo,
        "Datas (Zero à Esquerda)": comuns.auditar_data_sem_zero_esquerda,
        "Siglas (Uso do travessão)": comuns.auditar_uso_siglas,
        "Incisos (Pontuação)": comuns.auditar_pontuacao_incisos,
        "Alíneas (Pontuação)": comuns.auditar_pontuacao_alineas,
        
        # Regras de Anexo
        "Anexo (Identificação)": anexo.auditar_anexo, 
        "Anexo: Sequência de Capítulos": anexo.auditar_sequencia_capitulos_anexo,
        "Anexo: Sequência de Seções": anexo.auditar_sequencia_secoes_anexo,
        "Anexo: Sequência de Artigos": anexo.auditar_sequencia_artigos_anexo,
        "Anexo: Pontuação Hierárquica": anexo.auditar_pontuacao_hierarquica_anexo,
    }

    # 2. Regras Específicas
    if tipo == "CEG":
        regras["Epígrafe (CEG/MIDR)"] = ceg.auditar_epigrafe_ceg
        regras["Preâmbulo (CEG)"] = ceg.auditar_preambulo_ceg
        
    elif tipo == "CONDEL":
        regras["Cabeçalho (MINISTÉRIO/CONSELHO)"] = condel.auditar_cabecalho_condel
        regras["Epígrafe (CONDEL)"] = condel.auditar_epigrafe_condel
        regras["Preâmbulo (CONDEL)"] = condel.auditar_preambulo_condel
        
    return regras, tipo