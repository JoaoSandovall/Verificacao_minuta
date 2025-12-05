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
        "Ementa (Verbo Inicial)": comuns.auditar_ementa,
        "Bloco de Assinatura": comuns.auditar_assinatura,
        "Fecho de Vigência": comuns.auditar_fecho_vigencia,
        "Artigos (Formato Numeração)": comuns.auditar_numeracao_artigos,
        "Parágrafos (§ Espaçamento)": comuns.auditar_espacamento_paragrafo,
        "Datas (Zero à Esquerda)": comuns.auditar_data_sem_zero_esquerda,
        "Siglas (Uso do travessão)": comuns.auditar_uso_siglas,
        "Anexo (Identificação)": anexo.auditar_anexo, 
        "Anexo: Sequência de Capítulos": anexo.auditar_sequencia_capitulos_anexo,
        "Anexo: Sequência de Seções": anexo.auditar_sequencia_secoes_anexo,
        "Anexo: Sequência de Artigos": anexo.auditar_sequencia_artigos_anexo,
        "Anexo: Pontuação Hierárquica": anexo.auditar_pontuacao_hierarquica_anexo,
    }

    # 2. Regras Específicas (Injeção de Dependência)
    if tipo == "CEG":
        regras["Brasão / Cabeçalho (CEG)"] = ceg.auditar_cabecalho_ceg
        regras["Epígrafe (CEG/MIDR)"] = ceg.auditar_epigrafe_ceg
        regras["Preâmbulo (CEG)"] = ceg.auditar_preambulo_ceg
        
    else:
        
        label_tipo = tipo if tipo != "DESCONHECIDO" else "CONDEL"
        
        regras["Brasão / Ministério"] = condel.auditar_cabecalho_condel
        regras[f"Epígrafe ({label_tipo})"] = condel.auditar_epigrafe_condel
        regras[f"Preâmbulo ({label_tipo})"] = condel.auditar_preambulo_condel
        regras["Incisos (Pontuação Estrita)"] = comuns.auditar_pontuacao_incisos 
        regras["Alíneas (Pontuação Estrita)"] = comuns.auditar_pontuacao_alineas

    return regras, tipo