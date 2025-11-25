from .regras.comuns import (
    auditar_cabecalho_ministerio,
    auditar_numeracao_artigos,
    auditar_espacamento_paragrafo,
    auditar_data_sem_zero_esquerda,
    auditar_uso_siglas
)

from .regras.resolucao import (
    auditar_epigrafe,
    auditar_ementa,
    auditar_preambulo,
    auditar_pontuacao_incisos,
    auditar_pontuacao_alineas,
    auditar_fecho_vigencia,
    auditar_assinatura
)

from .regras.anexo import (
    auditar_anexo,
    auditar_sequencia_capitulos_anexo,
    auditar_sequencia_secoes_anexo,
    auditar_sequencia_artigos_anexo,
    auditar_pontuacao_hierarquica_anexo
)

TODAS_AS_AUDITORIAS = {
    # --- Regras Gerais (Aplicadas na Resolução) ---
    "Brasão / Nome do Ministério": auditar_cabecalho_ministerio,
    "Epígrafe (Formato e Data)": auditar_epigrafe,
    "Ementa (Verbo Inicial)": auditar_ementa,
    "Preâmbulo (Estrutura)": auditar_preambulo,
    "Bloco de Assinatura": auditar_assinatura,
    "Fecho de Vigência": auditar_fecho_vigencia,
    
    # --- Regras de Formatação
    "Artigos (Formato Numeração)": auditar_numeracao_artigos,
    "Parágrafos (§ Espaçamento)": auditar_espacamento_paragrafo,
    "Datas (Zero à Esquerda no Dia)": auditar_data_sem_zero_esquerda,
    "Siglas (Uso do travessão)": auditar_uso_siglas,

    # --- Regras Estritas (Apenas Resolução) ---
    "Incisos (Pontuação - Resolução)": auditar_pontuacao_incisos,
    "Alíneas (Pontuação - Resolução)": auditar_pontuacao_alineas,

    # --- Regra de Divisão ---
    "Anexo (Identificação)": auditar_anexo,

    # --- Regras Específicas (Apenas Anexo) ---
    "Anexo: Sequência de Capítulos": auditar_sequencia_capitulos_anexo,
    "Anexo: Sequência de Seções": auditar_sequencia_secoes_anexo,
    "Anexo: Sequência de Artigos": auditar_sequencia_artigos_anexo,
    "Anexo: Pontuação Hierárquica": auditar_pontuacao_hierarquica_anexo,
}