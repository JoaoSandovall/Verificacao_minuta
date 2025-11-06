🔎 Auditor de Minutas de Resolução
Este projeto é uma ferramenta de software, desenvolvida em Python e Streamlit, destinada a automatizar a verificação de conformidade de documentos normativos, como minutas de resoluções.

A aplicação analisa o texto de documentos em busca de padrões de formatação e estrutura definidos em um conjunto de regras de negócio, baseadas em manuais de redação e boas práticas. O objetivo é fornecer um feedback instantâneo para o usuário, agilizando o processo de revisão e garantindo a padronização dos documentos.

✨ Funcionalidades Principais
Interface Web Simples: Utiliza o Streamlit para criar uma aplicação web interativa e de fácil uso.

Duas Formas de Entrada: O usuário pode colar o texto diretamente na interface ou fazer o upload de um arquivo nos formatos .txt, .docx ou .pdf.

Limpeza Automática: O sistema identifica e remove automaticamente marcas d'água comuns (como * MINUTA DE DOCUMENTO) antes de iniciar a análise.

Análise Estrutural (Resolução vs. Anexo): A ferramenta detecta inteligentemente a separação do corpo principal da resolução e do seu ANEXO, aplicando um conjunto de regras específicas de formatação para cada parte.

Relatório Imediato: Os resultados da auditoria são exibidos instantaneamente, divididos em "👎 Itens com Erros" e "👍 Itens Corretos", com detalhes sobre cada falha encontrada.

📋 Regras de Auditoria Implementadas
O auditor verifica 12 regras principais, agrupadas por seção do documento:

1. Cabeçalho
Brasão / Nome do Ministério: Valida se o documento começa exatamente com MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL.

Epígrafe (Formato e Data): Checa a estrutura da epígrafe (ex: RESOLUÇÃO CONDEL Nº ...), garantindo que esteja em maiúsculas (incluindo o mês) e que a data seja válida.

Ementa (Verbo Inicial): Garante que o parágrafo da ementa comece com um verbo de ação aceito (ex: "Aprova", "Altera", "Dispõe", "Regulamenta", etc.).

2. Corpo da Resolução
Preâmbulo (Estrutura): Analisa o preâmbulo, verificando se ele inicia com uma das autoridades válidas (ex: O PRESIDENTE DO CONSELHO DELIBERATIVO...) e se termina exatamente com a palavra RESOLVEU: em maiúsculas.

Artigos (Numeração): Confere a formatação e o espaçamento da numeração dos artigos, exigindo:

Art. N° (ordinal º e dois espaços) para artigos de 1 a 9.

Art. NN. (ponto . e dois espaços) para artigos de 10 em diante.

Parágrafos (§ Espaçamento): Verifica se o símbolo de parágrafo (§) é seguido por exatamente dois espaços.

Incisos (Pontuação): Valida a sequência de numerais romanos (I, II, III...) e a pontuação final de cada inciso (uso de ;, :, ; e para o penúltimo, e . para o último).

Alíneas (Pontuação): Valida a sequência de letras (a, b, c...) e a pontuação final de cada alínea (uso de ;, ; e para a penúltima, e . para a última).

Siglas (Uso do travessão): Procura por siglas formatadas incorretamente entre parênteses (ex: (SIGLA)) e recomenda o uso de travessão.

3. Rodapé e Anexo
Bloco de Assinatura: Checa se o bloco de assinatura segue o padrão de NOME DO SIGNATÁRIO (em maiúsculas) seguido pelo Cargo (em capitalização normal).

Fecho de Vigência: Verifica se a cláusula de vigência corresponde exatamente a um dos dois padrões permitidos:

Esta Resolução entra em vigor na data de sua publicação.

Esta Resolução entra em vigor em [dia]º de [mês minúsculo] de [ano].

Anexo: Identifica se a linha de separação ANEXO existe e está formatada corretamente (sozinha na linha e em maiúsculas).

🚀 Como Executar o Projeto Localmente
Siga os passos abaixo para instalar e rodar a aplicação em seu computador.

Pré-requisitos
Python 3.9 ou superior

Git

Instalação
Clone o repositório para sua máquina local:

Bash

git clone https://github.com/JoaoSandovall/Verificacao_minuta.git
Navegue até a pasta do projeto:

Bash

cd Verificacao_minuta
Crie e ative um ambiente virtual (recomendado):

Bash

# Criar o ambiente
python -m venv .venv

# Ativar no Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Ativar no Windows (Cmd)
.\.venv\Scripts\activate

# Ativar no Linux/Mac
source .venv/bin/activate
Instale as dependências do projeto listadas no arquivo requirements.txt:

Bash

pip install -r requirements.txt
Execução
Com o ambiente virtual ativo e as dependências instaladas, inicie a aplicação Streamlit com o seguinte comando:

Bash

streamlit run app.py
O seu navegador web abrirá automaticamente no endereço local (geralmente http://localhost:8501), exibindo a aplicação pronta para uso.
