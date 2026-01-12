from .regras import estrutura, resolucao, anexo
from .regras.orgaos import condel, ceg, coaride, cnrh

def identificar_tipo_resolucao(texto):
    if not texto: 
        return "DESCONHECIDO"
    
    inicio = texto[:1000].upper()
    
    if "RESOLUÇÃO CEG" in inicio or "CEG/MIDR" in inicio:
        return "CEG"
    elif "RESOLUÇÃO CONDEL" in inicio or "CONDEL/SUDECO" in inicio:
        return "CONDEL"
    elif "RESOLUÇÃO COARIDE" in inicio:
        return "COARIDE"
    elif "CNRH" in inicio:
        return "CNRH"
    
    return "DESCONHECIDO"

def obter_regras_anexo():

    return {
        "Anexo (Identificação)": anexo.auditar_anexo, 
        "Anexo: Sequência de Capítulos": anexo.auditar_sequencia_capitulos_anexo,
        "Anexo: Sequência de Seções": anexo.auditar_sequencia_secoes_anexo,
        "Anexo: Sequência de Artigos": anexo.auditar_sequencia_artigos_anexo,
        "Anexo: Sequência de Parágrafos": anexo.auditar_sequencia_paragrafos_anexo,
        "Anexo: Pontuação Hierárquica": anexo.auditar_pontuacao_hierarquica_anexo,
        "Artigos (Formato)": estrutura.auditar_formatacao_artigos,
        "Parágrafos (Espaçamento)": estrutura.auditar_formatacao_paragrafo,
        "Siglas": estrutura.auditar_uso_siglas,
        "Incisos (Sequência)": estrutura.auditar_sequencia_incisos,
        "Incisos (Pontuação)": estrutura.auditar_pontuacao_incisos,
        "Alíneas (Pontuação)": estrutura.auditar_formatacao_alineas
    }

def obter_regras(texto_completo):

    tipo = identificar_tipo_resolucao(texto_completo)
    
    # 1. Regras Comuns (Base)
    regras = {
        "Cabeçalho (Genérico)": resolucao.auditar_cabecalho,
        "Ementa": resolucao.auditar_ementa,
        "Verbo Art. 1º": resolucao.auditar_verbo_primeiro_artigo,
        "Assinatura": resolucao.auditar_assinatura,
        "Vigência": resolucao.auditar_fecho_vigencia,
        # Regras de Formatação GERAL
        "Artigos": estrutura.auditar_formatacao_artigos,
        "Parágrafos": estrutura.auditar_formatacao_paragrafo,
        "Datas": estrutura.auditar_data,
        "Siglas": estrutura.auditar_uso_siglas,
        "Incisos (Pontuação)": estrutura.auditar_pontuacao_incisos,
        "Incisos (Sequência)": estrutura.auditar_sequencia_incisos,
        "Alíneas": estrutura.auditar_formatacao_alineas,
    }

    # 2. Regras Específicas
    if tipo == "CEG":
        regras["Cabeçalho (MINISTÉRIO/COMITÊ)"] = ceg.auditar_cabecalho_ceg
        regras["Epígrafe (CEG/MIDR)"] = ceg.auditar_epigrafe_ceg
        regras["Preâmbulo (CEG)"] = ceg.auditar_preambulo_ceg
        
    elif tipo == "CONDEL":
        regras["Cabeçalho (MINISTÉRIO/CONSELHO)"] = condel.auditar_cabecalho_condel
        regras["Epígrafe (CONDEL)"] = condel.auditar_epigrafe_condel
        regras["Preâmbulo (CONDEL)"] = condel.auditar_preambulo_condel
        
    elif tipo == "COARIDE":
        regras["Epígrafe (COARIDE)"] = coaride.auditar_epigrafe_coaride
        regras["Preâmbulo (COARIDE)"] = coaride.auditar_preambulo_coarides
        
    elif tipo == "CNRH":        
        regras["Cabeçalho (MINISTÉRIO/CONSELHO)"] = cnrh.auditar_cabecalho_cnrh
        regras["Epígrafe (CNRH)"] = cnrh.auditar_epigrafe_cnrh
        regras["Preâmbulo (CNRH)"] = cnrh.auditar_preambulo_cnrh
    
    return regras, tipo