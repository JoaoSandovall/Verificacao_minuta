# 🔎 Auditor de Minutas de Resolução

Ferramenta em Python e Streamlit para validar automaticamente a formatação de minutas de resolução, com base em um conjunto de regras de redação e estilo.

## ✨ Funcionalidades

* **Interface Web:** Aplicação simples e interativa.
* **Entrada Dupla:** Aceita texto colado ou upload de arquivos (`.txt`, `.docx`, `.pdf`).
* **Análise Estrutural:** Identifica a separação entre a Resolução e o `ANEXO`, aplicando regras de formatação específicas para cada parte.
* **Relatório Imediato:** Mostra instantaneamente os "Itens com Erros" e "Itens Corretos".
* **Limpeza Automática:** Remove marcas d'água (ex: "MINUTA DE DOCUMENTO") antes da análise.

## 📋 Regras de Auditoria Implementadas

### Cabeçalho
1.  **Brasão / Nome do Ministério:** Valida se o documento começa com `MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL`.
2.  **Epígrafe (Formato e Data):** Checa a estrutura `RESOLUÇÃO CONDEL Nº ...`, exigindo maiúsculas (incluindo o mês) e validando a data.
3.  **Ementa (Verbo Inicial):** Garante que a ementa comece com um verbo de ação aceito (ex: "Aprova", "Altera", "Dispõe").

### Corpo da Resolução
4.  **Preâmbulo (Estrutura):** Analisa o preâmbulo, verificando se inicia com a autoridade correta (ex: `O PRESIDENTE DO CONSELHO...`) e se termina exatamente com `RESOLVEU:`.
5.  **Artigos (Numeração):** Confere o padrão de numeração:
    * `Art. 1º ` (com `º` e dois espaços).
    * `Art. 10. ` (com `.` e dois espaços).
6.  **Parágrafos (§ Espaçamento):** Verifica se o símbolo `§` é seguido por exatamente dois espaços.
7.  **Incisos (Pontuação):** Valida a sequência de numerais romanos (I, II, III...) e a pontuação correta (`;`, `: (para alíneas)`, `; e (penúltimo)`, `. (último)`).
8.  **Alíneas (Pontuação):** Valida a sequência de letras (a, b, c...) e a pontuação correta (`;`, `; e (penúltima)`, `. (última)`).
9.  **Siglas (Uso do travessão):** Procura por siglas incorretamente formatadas entre parênteses, ex: `(SIGLA)`.

### Rodapé e Anexo
10. **Bloco de Assinatura:** Checa o padrão `NOME DO SIGNATÁRIO` (maiúsculas) seguido pelo `Cargo` (normal).
11. **Fecho de Vigência:** Verifica se a cláusula corresponde *exatamente* a um dos padrões:
    * `Esta Resolução entra em vigor na data de sua publicação.`
    * `Esta Resolução entra em vigor em [dia]º de [mês minúsculo] de [ano].`
12. **Anexo:** Identifica se a linha `ANEXO` está formatada corretamente (sozinha, em maiúsculas).

## 🚀 Como Executar Localmente

### Pré-requisitos
* [Python 3.9+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)

### Instalação

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/JoaoSandovall/Verificacao_minuta.git](https://github.com/JoaoSandovall/Verificacao_minuta.git)
    ```

2.  Acesse a pasta do projeto:
    ```bash
    cd Verificacao_minuta
    ```

3.  Crie e ative um ambiente virtual:
    ```bash
    # Criar o ambiente
    python -m venv .venv
    
    # Ativar (Windows)
    .\.venv\Scripts\Activate.ps1
    
    # Ativar (Linux/Mac)
    source .venv/bin/activate
    ```

4.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Execução

1.  Inicie a aplicação Streamlit:
    ```bash
    streamlit run app.py
    ```

2.  Abra o seu navegador no endereço `http://localhost:8501`.
