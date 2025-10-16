# core/regras/__init__.py

from .regras_cabecalho import auditar_cabecalho_ministerio, auditar_epigrafe, auditar_ementa
from .regras_corpo import auditar_preambulo, auditar_numeracao_artigos, auditar_pontuacao_incisos, auditar_uso_siglas, auditar_pontuacao_alineas
from .regras_rodape import auditar_assinatura, auditar_fecho_vigencia
from .regras_anexo import auditar_anexo

# Dicionário central com todas as auditorias disponíveis na aplicação
TODAS_AS_AUDITORIAS = {
    "Brasão / Nome do Ministério": auditar_cabecalho_ministerio,
    "Epígrafe (Formato e Data)": auditar_epigrafe,
    "Ementa (Verbo Inicial)": auditar_ementa,
    "Preâmbulo (Estrutura)": auditar_preambulo,
    "Artigos (Numeração)": auditar_numeracao_artigos,
    "Incisos (Pontuação)": auditar_pontuacao_incisos,
    "Alíneas (Pontuação)": auditar_pontuacao_alineas,
    "Siglas (Uso do travessão)": auditar_uso_siglas,
    "Bloco de Assinatura": auditar_assinatura,
    "Fecho de Vigência": auditar_fecho_vigencia,
    "Anexo": auditar_anexo,
}