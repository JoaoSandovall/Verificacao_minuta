# Auditor de Minutas de Resolução

Este projeto é uma ferramenta desenvolvida em Python com a biblioteca Streamlit para automatizar a verificação de conformidade de documentos, como minutas de resoluções, com base em um conjunto de regras de formatação e estilo pré-definidas.

A aplicação permite que o usuário envie um documento (em formato `.pdf`, `.docx` ou `.txt`) ou cole o texto diretamente em uma interface web amigável, recebendo um relatório instantâneo dos itens que estão em conformidade e daqueles que contêm erros.

## ✨ Funcionalidades

* **Interface Web Interativa:** Utiliza o Streamlit para criar uma experiência de usuário simples e intuitiva.
* **Múltiplos Formatos de Entrada:** Suporta o upload de arquivos `.pdf`, `.docx` e `.txt`, além de permitir que o texto seja colado diretamente na página.
* **Análise Separada de Resolução e Anexo:** O sistema identifica de forma inteligente a divisão entre o corpo principal da resolução e seu anexo, aplicando conjuntos de regras específicas para cada parte.
* **Filtro de Regras Dinâmico:** Uma barra lateral permite ao usuário selecionar e desmarcar quais regras de auditoria deseja aplicar, tornando a análise flexível para diferentes tipos de documentos.
* **Resultados Claros e Organizados:** O relatório de auditoria é apresentado em duas colunas ("Itens com Erros" e "Itens Corretos"), facilitando a identificação dos pontos que necessitam de correção.

## 📋 Regras Implementadas

Atualmente, o auditor verifica a conformidade dos seguintes itens:

* **Brasão / Nome do Ministério:** Valida se o cabeçalho do ministério está presente e formatado corretamente.
* **Epígrafe (Formato e Data):** Checa a estrutura da linha de título da resolução, incluindo a formatação da data.
* **Ementa (Verbo Inicial):** Garante que o parágrafo de resumo comece com um verbo de ação apropriado.
* **Preâmbulo (Estrutura):** Analisa a estrutura do preâmbulo, verificando a presença da autoridade e da palavra "RESOLVE:".
* **Artigos (Numeração):** Confere se a numeração dos artigos segue o padrão ordinal (até 9º) e cardinal (a partir do 10).
* **Incisos (Pontuação):** Valida a pontuação correta (`;`, `:`, `.`) no final dos incisos.
* **Siglas (Uso do travessão):** Verifica se as siglas são introduzidas corretamente, sem o uso de parênteses.
* **Bloco de Assinatura:** Checa a formatação do bloco de assinatura, garantindo que o nome do signatário esteja em maiúsculas.
* **Fecho de Vigência:** Procura pela cláusula padrão de entrada em vigor da resolução.
* **Anexo:** Identifica a presença e a formatação da seção "ANEXO".

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para instalar e rodar a aplicação em seu computador.

### Pré-requisitos

* Python 3.9 ou superior
* Git

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/JoaoSandovall/Verificacao_minuta.git](https://github.com/JoaoSandovall/Verificacao_minuta.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd Verificacao_minuta
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    # Crie o ambiente
    python -m venv .venv

    # Ative o ambiente (Windows)
    .\.venv\Scripts\Activate.ps1

    # Ative o ambiente (Linux/Mac)
    # source .venv/bin/activate
    ```

4.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas que o projeto precisa. Instale todas de uma vez com o comando:
    ```bash
    pip install -r requirements.txt
    ```

### Execução

Com o ambiente virtual ativo e as dependências instaladas, inicie a aplicação com o seguinte comando:

```bash
streamlit run app.py
```

Seu navegador web abrirá automaticamente com a aplicação pronta para ser usada.
