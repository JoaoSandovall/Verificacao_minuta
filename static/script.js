const API_URL = "/auditar"; // Usa caminho relativo para evitar erro de CORS/Porta
let modoArquivo = false;

function abrirTab(tipo) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('ativa'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('ativa'));
    document.getElementById(`tab-${tipo}`).classList.add('ativa');
    event.target.classList.add('ativa');
    modoArquivo = (tipo === 'arquivo');
}

function mostrarRevisao() {
    document.getElementById('tela-editor').classList.remove('ativa');
    document.getElementById('tela-revisao').classList.add('ativa');
}

function voltarEditor() {
    document.getElementById('tela-revisao').classList.remove('ativa');
    document.getElementById('tela-editor').classList.add('ativa');
    // Limpa tudo ao voltar
    document.getElementById('documento-renderizado').innerHTML = "";
    document.getElementById('erros-resolucao-lista').innerHTML = "";
    document.getElementById('erros-anexo-lista').innerHTML = "";
    document.getElementById('grupo-resolucao').style.display = "none";
    document.getElementById('grupo-anexo').style.display = "none";
    document.getElementById('msg-sucesso').style.display = "none";
}

async function analisarTexto() {
    let textoParaEnviar = "";
    if (modoArquivo) {
        alert("Para testar, por favor copie e cole o texto na aba 'Colar Texto'.");
        return;
    } else {
        textoParaEnviar = document.getElementById('input-texto').value;
    }

    if (!textoParaEnviar.trim()) { alert("O texto está vazio."); return; }

    const btn = document.querySelector('.btn-primario');
    const textoOriginal = btn.innerText;
    btn.innerText = "⏳ Analisando...";
    btn.disabled = true;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ texto: textoParaEnviar })
        });
        if (!response.ok) throw new Error("Erro na API");
        const data = await response.json();
        
        renderizarResultado(data);
        mostrarRevisao();
    } catch (error) {
        console.error(error);
        alert("Erro ao conectar com o servidor.");
    } finally {
        btn.innerText = textoOriginal;
        btn.disabled = false;
    }
}

function renderizarResultado(data) {
    document.getElementById('tipo-documento-badge').innerText = "Tipo: " + data.tipo_documento;
    document.getElementById('documento-renderizado').innerHTML = data.html;

    const listaRes = document.getElementById('erros-resolucao-lista');
    const listaAnx = document.getElementById('erros-anexo-lista');
    const grupoRes = document.getElementById('grupo-resolucao');
    const grupoAnx = document.getElementById('grupo-anexo');
    const msgSucesso = document.getElementById('msg-sucesso');

    // Reset visual
    listaRes.innerHTML = "";
    listaAnx.innerHTML = "";
    grupoRes.style.display = "none";
    grupoAnx.style.display = "none";
    msgSucesso.style.display = "none";

    if (data.erros.length === 0) {
        msgSucesso.style.display = "block";
        return;
    }

    let temErroRes = false;
    let temErroAnx = false;

    data.erros.forEach(erro => {
        const card = document.createElement('div');
        card.className = 'card-erro';
        
        let btnHtml = "";
        if (erro.tem_link) {
            btnHtml = `<div class="btn-ir" onclick="rolarParaErro('${erro.id}')">🎯 Ver no Texto</div>`;
        }

        card.innerHTML = `
            <div class="card-titulo">${erro.regra}</div>
            <div class="card-msg">${erro.mensagem}</div>
            ${btnHtml}
        `;

        if (erro.contexto === "Resolução") {
            listaRes.appendChild(card);
            temErroRes = true;
        } else {
            listaAnx.appendChild(card);
            temErroAnx = true;
        }
    });

    // Só mostra os títulos se houver erros naquela seção
    if (temErroRes) grupoRes.style.display = "block";
    if (temErroAnx) grupoAnx.style.display = "block";
}

function rolarParaErro(id) {
    const elemento = document.getElementById(id);
    if (elemento) {
        document.querySelectorAll('mark.focado').forEach(el => el.classList.remove('focado'));
        elemento.classList.add('focado');
        elemento.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}