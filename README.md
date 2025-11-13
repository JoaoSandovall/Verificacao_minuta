# 🔎 Auditor de Minutas de Resolução

Ferramenta em Python e Streamlit para validar automaticamente a formatação de minutas de resolução, com base em um conjunto de regras de redação e estilo.

## ✨ Funcionalidades

* **Interface Web:** Aplicação simples e interativa.
* **Entrada Dupla:** Aceita texto colado ou upload de arquivos (`.txt`, `.docx`, `.pdf`).
* **Análise Estrutural Inteligente:** Identifica a separação entre a **Resolução Principal** e o **Anexo**, aplicando conjuntos de regras de pontuação e sequência completamente diferentes para cada parte.
* **Relatório Imediato:** Mostra instantaneamente os "Itens com Erros" e "Itens Corretos".
* **Limpeza Automática:** Remove marcas d'água (ex: "MINUTA DE DOCUMENTO") antes da análise.

## 📋 Regras de Auditoria Implementadas

A análise é dividida em três partes: regras que se aplicam a todo o documento, regras estritas para a Resolução e regras hierárquicas para o Anexo.

### Regras Gerais (Aplicadas em Todo o Documento)

1.  **Brasão / Nome do Ministério:** Valida se o documento começa com `MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL`.
2.  **Epígrafe (Formato e Data):** Checa a estrutura `(MINUTA )?RESOLUÇÃO CONDEL... Nº ...`.
    * Permite variações como `CONDEL/SUDECO` ou `CONDEL/SUDENE`.
    * Aceita `xx` (maiúsculo ou minúsculo) no lugar do número, dia ou mês.
    * Verifica se o mês (se não for `xx`) está em MAIÚSCULO e se a data é válida.
3.  **Ementa (Verbo Inicial):** Garante que a ementa comece com um verbo de ação aceito (ex: "Aprova", "Altera", "Dispõe").
4.  **Artigos (Formato Numeração):** Valida o formato dos artigos que **iniciam uma linha**:
    * **Art. 1° a 9°:** Devem usar o símbolo de grau (`°`) e ser seguidos por dois espaços (ex: `Art. 1°  `). O uso do ordinal `º` é marcado como erro.
    * **Art. 10. em diante:** Devem usar ponto (`.`) e ser seguidos por dois espaços (ex: `Art. 10.  `).
5.  **Parágrafos (§ Espaçamento):** Valida que o símbolo `§` (Parágrafo), quando **inicia uma linha**, é seguido por exatamente dois espaços (ex: `§ 1°  `).
6.  **Datas (Zero à Esquerda):** Procura por datas no formato "dd de mês de aaaa" (ex: "09 de setembro de 2025") e reporta um erro, sugerindo a forma correta ("9 de setembro de 2025").
7.  **Siglas (Uso do travessão):** Procura por siglas formatadas incorretamente entre parênteses, ex: `(SIGLA)`.
8.  **Anexo (Identificação):** Valida se a linha `ANEXO` está formatada corretamente (sozinha, em maiúsculas).

### Regras da Resolução Principal

(Aplicadas apenas ao texto **antes** da linha `ANEXO`)

1.  **Preâmbulo (Estrutura):** Verifica se o parágrafo do preâmbulo começa com uma das Autoridades (`O PRESIDENTE...`) e termina exatamente com a frase `o Colegiado resolveu:` (em minúsculo).
2.  **Bloco de Assinatura:** Valida se o bloco de assinatura contém **apenas** o nome do signatário em maiúsculas (ex: `ANTONIO WALDEZ GÓES DA SILVA`) e se **não há** linhas de cargo abaixo dele.
3.  **Fecho de Vigência:** Verifica se a cláusula corresponde exatamente a um dos padrões:
    * `Esta Resolução entra em vigor na data de sua publicação.`
    * `Esta Resolução entra em vigor em [dia]° de [mês minúsculo] de [ano].`
4.  **Incisos (Pontuação Estrita):** Valida a sequência (I, II, III...) e a pontuação estrita: `;` para itens intermediários, `; e` para o penúltimo, e `.` para o último.
5.  **Alíneas (Pontuação Estrita):** Valida a sequência (a, b, c...) e a pontuação estrita: `;` para itens intermediários, `; e` para o penúltimo, e `.` para o último.

### Regras Específicas do Anexo

(Aplicadas apenas ao texto **depois** da linha `ANEXO`)

1.  **Sequência de Capítulos:** Valida se a numeração romana (I, II, III...) dos `CAPÍTULOS` é contínua e não pula números.
2.  **Sequência de Seções:** Valida se a numeração romana (I, II, III...) das `Seções` **reinicia** corretamente dentro de cada novo Capítulo.
3.  **Sequência de Artigos:** Valida se a numeração (1°, 2°, 3°... 10., 11...) dos `Art.` é contínua do início ao fim do Anexo.
4.  **Pontuação Hierárquica:** Substitui as regras estritas por uma lógica inteligente que entende o contexto:
    * **Regra de Abertura (`:`)**: Verifica se Artigos, Parágrafos ou Incisos que abrem uma nova subdivisão (ex: um Art. seguido por Incisos) terminam corretamente com dois-pontos.
    * **Regra de Declaração (`.`)**: Verifica se Artigos e Parágrafos que são declarações únicas (não abrem listas) terminam com ponto final.
    * **Regra de Lista (`;`, `; e`, `; ou`, `.`)**: Verifica Incisos e Alíneas com base no que vem *depois*. Por exemplo, uma alínea `b)` seguida por um `Inciso III` pode terminar com `;`, enquanto uma alínea `b)` seguida por um `§ 1º` deve terminar com `.`.

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

## 🐞 Solução de Erros (Streamlit Cloud)

Se você ver um erro sobre `locale 'pt_BR.UTF-8' não encontrado` ao fazer o deploy no Streamlit Cloud, é porque o servidor Linux padrão não possui o pacote de idioma português.

**Solução:** Este repositório já inclui um arquivo `packages.txt` com o conteúdo `locales-all`. O Streamlit irá ler este arquivo automaticamente e instalar todos os pacotes de idioma necessários, corrigindo o erro.
