# Auditor de Minutas de Resolução

Ferramenta automatizada para validação de conformidade estrutural e redacional de atos normativos (Resoluções CONDEL/SUDECO e CEG/MIDR), alinhada às diretrizes do Decreto nº 12.002/2024.

## Tecnologias Utilizadas

### Backend
* **Python 3.9+**: Linguagem base do projeto.
* **FastAPI**: Framework web moderno e de alta performance para construção da API.
* **Uvicorn**: Servidor ASGI para execução da aplicação FastAPI.
* **Pydantic**: Validação de dados e parsing de modelos de entrada.
* **Expressões Regulares (RegEx)**: Motor principal de análise léxica e sintática das minutas.

### Processamento de Arquivos
* **python-docx**: Extração de texto de arquivos Word (.docx).
* **PyPDF2**: Extração de texto de arquivos PDF (.pdf).
* **Pandas**: Manipulação de dados estruturados (suporte auxiliar).

### Frontend
* **HTML5**: Estruturação semântica da interface.
* **CSS3**: Estilização visual e layout responsivo (visual de documento oficial).
* **JavaScript (ES6+)**: Lógica de interação, consumo da API (Fetch API) e manipulação do DOM para destaque de erros e navegação.

---

## Estrutura do Projeto

```text
/
├── api.py                  # Ponto de entrada da aplicação (Servidor FastAPI)
├── core/                   # Núcleo de lógica de validação
│   ├── __init__.py         # Factory pattern para seleção dinâmica de regras
│   ├── utils.py            # Funções auxiliares (conversão de romanos, etc.)
│   └── regras/             # Módulos de auditoria específicos
│       ├── comuns.py       # Regras compartilhadas (artigos, parágrafos, datas)
│       ├── condel.py       # Regras específicas do CONDEL
│       ├── ceg.py          # Regras específicas do CEG
│       └── anexo.py        # Validação estrutural de anexos
├── static/                 # Frontend da aplicação
│   ├── index.html          # Interface do usuário
│   ├── styles.css          # Folhas de estilo
│   └── script.js           # Lógica do cliente
├── requirements.txt        # Dependências Python
├── packages.txt            # Dependências do sistema (locales)
└── vercel.json             # Configuração de deploy (Vercel)

```
## Instalação e Execução

### Pré-requisitos
* Python 3.9 ou superior instalado.
* Git instalado.

### Passos para execução local

1.  **Clone o repositório:**
    ```bash
    git clone [URL_DO_REPOSITORIO]
    cd Verificacao_minuta
    ```

2.  **Configure o ambiente virtual:**
    * **Windows:**
        ```bash
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        ```
    * **Linux/Mac:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o servidor:**
    ```bash
    uvicorn api:app --reload
    ```

5.  **Acesse a aplicação:**
    Abra o navegador em `http://127.0.0.1:8000`.

## Deploy (Vercel)

O projeto está configurado para deploy serverless na Vercel através do arquivo `vercel.json`. O backend (`api.py`) é executado como uma Serverless Function e também serve os arquivos estáticos do frontend.
