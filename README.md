Auditor de Minutas de Resolução
Este projeto é uma ferramenta desenvolvida em Python com a biblioteca Streamlit para automatizar a verificação de conformidade de documentos, como minutas de resoluções, com base em um conjunto de regras de formatação e estilo pré-definidas.

A aplicação permite que o usuário cole o texto diretamente ou envie um documento (em formato .pdf, .docx ou .txt), recebendo um relatório instantâneo dos itens que estão em conformidade e daqueles que contêm erros, facilitando a revisão.

✨ Funcionalidades
Interface Web Interativa: Utiliza o Streamlit para criar uma experiência de usuário simples e direta, com abas para "Colar Texto" e "Anexar Arquivo".

Múltiplos Formatos de Entrada: Suporta a extração de texto de arquivos .pdf, .docx e .txt.

Análise Separada de Resolução e Anexo: O sistema identifica de forma inteligente a divisão entre o corpo principal da resolução e seu anexo (procurando pela linha ANEXO), aplicando conjuntos de regras específicas para cada parte.

Relatório Claro: Os resultados são apresentados em duas colunas ("Itens com Erros" e "Itens Corretos") para fácil identificação dos pontos que necessitam de correção.

Limpeza Rápida: Inclui um botão "Limpar" para apagar rapidamente o texto da caixa de entrada.

📋 Regras Implementadas
Atualmente, o auditor verifica a conformidade dos seguintes itens, com base nos arquivos em core/regras/:

Brasão / Nome do Ministério: Valida se o cabeçalho "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL" está presente e formatado corretamente.

Epígrafe (Formato e Data): Checa a estrutura da linha de título (ex: RESOLUÇÃO CONDEL Nº...), exigindo que esteja em maiúsculas, incluindo o mês, e valida a data.

Ementa (Verbo Inicial): Garante que o parágrafo de resumo (ementa) comece com um verbo de ação apropriado (ex: "Aprova", "Altera", "Dispõe").

Preâmbulo (Estrutura): Analisa a estrutura do preâmbulo, verificando a presença da autoridade ("O PRESIDENTE DO CONSELHO...") e a terminação exata com a palavra RESOLVE:.

Artigos (Numeração e Espaços): Confere se a numeração dos artigos segue o padrão correto:

Art. 1º (ordinal com dois espaços) para artigos de 1 a 9.

Art. 10. (ponto com dois espaços) para artigos de 10 em diante.

Parágrafos (§ Espaçamento): Verifica se o símbolo de parágrafo (§) é seguido por exatamente dois espaços (§ ).

Incisos (Sequência e Pontuação): Valida a sequência de numerais romanos (I, II, III...) e a pontuação correta (;, : para alíneas, ; e para o penúltimo, e . para o último).

Alíneas (Sequência e Pontuação): Valida a sequência de letras (a, b, c...) e a pontuação correta (;, ; e para a penúltima, e . para a última).

Siglas (Uso do travessão): Procura por siglas incorretamente formatadas (ex: (SIGLA)) e sugere o uso de travessão.

Bloco de Assinatura: Checa a formatação do bloco de assinatura, garantindo que o nome do signatário esteja em MAIÚSCULAS e o cargo abaixo.

Fecho de Vigência: Procura pelas duas cláusulas de vigência permitidas: "Esta Resolução entra em vigor na data de sua publicação." ou "Esta Resolução entra em vigor em [data específica].".

Anexo: Identifica se a linha ANEXO existe e está formatada corretamente (sozinha na linha, em maiúsculas).

🚀 Como Executar o Projeto Localmente
Siga os passos abaixo para instalar e rodar a aplicação em seu computador.

Pré-requisitos
Python 3.9 ou superior

Git

Instalação
Clone o repositório:

Bash

git clone https://github.com/JoaoSandovall/Verificacao_minuta.git
Navegue até a pasta do projeto:

Bash

cd Verificacao_minuta
Crie e ative um ambiente virtual:

Bash

# Crie o ambiente
python -m venv .venv

# Ative o ambiente (Windows - PowerShell)
.\.venv\Scripts\Activate.ps1

# Ative o ambiente (Windows - Cmd)
.\.venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
# source .venv/bin/activate
Instale as dependências: O arquivo requirements.txt contém todas as bibliotecas que o projeto precisa. Instale todas de uma vez com o comando:

Bash

pip install -r requirements.txt
Execução
Com o ambiente virtual ativo e as dependências instaladas, inicie a aplicação com o seguinte comando:

Bash

streamlit run app.py
Seu navegador web abrirá automaticamente com a aplicação pronta para ser usada.
