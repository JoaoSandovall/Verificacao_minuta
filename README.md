# Auditor de Minutas de Resolução

Ferramenta automatizada para validação de conformidade estrutural e redacional de atos normativos (Resoluções CONDEL/SUDECO, CEG/MIDR, COARIDE e CNRH), alinhada às diretrizes do Decreto nº 12.002/2024.

## Tecnologias Utilizadas

### Backend
* **Python 3.11+**: Linguagem base do projeto.
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
│   ├── auditor.py          # Processamento de texto e geração de anotações
│   ├── utils.py            # Funções auxiliares (conversão de romanos, etc.)
│   └── regras/             # Módulos de auditoria específicos
│       ├── estrutura.py    # Regras de formatação (artigos, parágrafos, siglas)
│       ├── resolucao.py    # Regras de conteúdo (cabeçalho, ementa, vigência)
│       ├── anexo.py        # Validação estrutural de anexos
│       └── orgaos/          # Regras específicas por autoridade
│           ├── condel.py   # Regras específicas do CONDEL/SUDECO
│           ├── ceg.py      # Regras específicas do CEG/MIDR
│           ├── coaride.py  # Regras específicas do COARIDE
│           └── cnrh.py     # Regras específicas do CNRH
├── static/                 # Frontend da aplicação
│   ├── index.html          # Interface do usuário
│   ├── styles.css          # Folhas de estilo
│   └── script.js           # Lógica do cliente
├── requirements.txt        # Dependências Python
└── vercel.json             # Configuração de deploy (Vercel)
```

## Instalação e Execução

### Pré-requisitos
* Python 3.11 ou superior instalado.
* Git instalado.

### Passos para execução local

1.  **Clone o repositório:**
    ```
    git clone [URL_DO_REPOSITORIO]
    cd Verificacao_minuta
    ```

2.  **Configure o ambiente virtual:**
    * **Windows:**
        ```
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        ```
    * **Linux/Mac:**
        ```
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```
    pip install -r requirements.txt
    ```

4.  **Execute o servidor:**
    ```
    uvicorn api:app --reload
    ```

5.  **Acesse a aplicação:**
    Abra o navegador em `http://127.0.0.1:8000`.
