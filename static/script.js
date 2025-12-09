const API_URL = "/auditar";
let modoArquivo = false;
let ultimosDados = null;

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
    document.getElementById('documento-renderizado').innerHTML = "";
    document.getElementById('erros-resolucao-lista').innerHTML = "";
    document.getElementById('erros-anexo-lista').innerHTML = "";
    document.getElementById('grupo-resolucao').style.display = "none";
    document.getElementById('grupo-anexo').style.display = "none";
    document.getElementById('msg-sucesso').style.display = "none";

    const btnMagic = document.getElementById('btn-corrigir-tudo');
    if (btnMagic) btnMagic.style.display = "none";
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
        
        ultimosDados = data;
        
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
    const btnCorrigirTudo = document.getElementById('btn-corrigir-tudo');

    listaRes.innerHTML = "";
    listaAnx.innerHTML = "";
    grupoRes.style.display = "none";
    grupoAnx.style.display = "none";
    msgSucesso.style.display = "none";
    
    if (btnCorrigirTudo) btnCorrigirTudo.style.display = "none";

    if (!data.erros || data.erros.length === 0) {
        msgSucesso.style.display = "block";
        return;
    }

    let temErroRes = false;
    let temErroAnx = false;
    let contaCorrigiveis = 0;

    data.erros.forEach(erro => {
        if (erro.correcao) contaCorrigiveis++;

        const card = document.createElement('div');
        card.className = 'card-erro';
        
        let botoesHtml = "";
        if (erro.tem_link) {
            botoesHtml += `<div class="btn-ir" onclick="rolarParaErro('${erro.id}')">🎯 Ver</div>`;
        }

        if (erro.correcao) {
            const originalEscaped = erro.correcao.original.replace(/"/g, '&quot;').replace(/'/g, "\\'");
            const novoEscaped = erro.correcao.novo.replace(/"/g, '&quot;').replace(/'/g, "\\'");
            
            botoesHtml += `
                <div class="btn-corrigir" onclick="aplicarCorrecao('${originalEscaped}', '${novoEscaped}')" style="margin-left:8px;">
                    ✨ Corrigir
                </div>
            `;
        }

        card.innerHTML = `
            <div class="card-titulo">${erro.regra}</div>
            <div class="card-msg">${erro.mensagem}</div>
            <div style="display:flex; margin-top:8px;">
                ${botoesHtml}
            </div>
        `;

        if (erro.contexto === "Resolução") {
            listaRes.appendChild(card);
            temErroRes = true;
        } else {
            listaAnx.appendChild(card);
            temErroAnx = true;
        }
    });

    if (temErroRes) grupoRes.style.display = "block";
    if (temErroAnx) grupoAnx.style.display = "block";

    if (contaCorrigiveis > 0 && btnCorrigirTudo) {
        btnCorrigirTudo.style.display = "inline-flex";
        btnCorrigirTudo.innerText = `✔️ Corrigir ${contaCorrigiveis} erros de parágrafo/artigo`;
    }
}

function rolarParaErro(id) {
    const elemento = document.getElementById(id);
    if (elemento) {
        document.querySelectorAll('mark.focado').forEach(el => el.classList.remove('focado'));
        elemento.classList.add('focado');
        elemento.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function aplicarCorrecao(original, novo) {
    const textarea = document.getElementById('input-texto');
    let textoAtual = textarea.value;

    if (textoAtual.includes(original)) {
        const textoNovo = textoAtual.replace(original, novo);
        textarea.value = textoNovo;
        analisarTexto();
    } else {
        alert("Não foi possível encontrar o trecho original. Talvez já tenha sido corrigido.");
    }
}

function corrigirTudoAutomaticamente() {
    if (!ultimosDados || !ultimosDados.erros) {
        alert("Nenhum dado de análise encontrado.");
        return;
    }

    const textarea = document.getElementById('input-texto');
    
    let texto = textarea.value.replace(/\r\n/g, '\n').replace(/\r/g, '\n'); 
    
    let correcoesAplicadas = 0;

    const errosCorrigiveis = ultimosDados.erros.filter(e => e.correcao && e.correcao.span);

    errosCorrigiveis.sort((a, b) => b.correcao.span[0] - a.correcao.span[0]);

    errosCorrigiveis.forEach(erro => {
        const [inicio, fim] = erro.correcao.span;
        const novoTexto = erro.correcao.novo;
        
        const textoOriginalNoLugar = texto.substring(inicio, fim);
    
        console.log(`[Correção] Regra: ${erro.regra}`);
        console.log(`Expected (Py): "${erro.correcao.original}"`);
        console.log(`Found    (JS): "${textoOriginalNoLugar}"`);

        if (textoOriginalNoLugar.trim() === erro.correcao.original.trim()) {
            texto = texto.slice(0, inicio) + novoTexto + texto.slice(fim);
            correcoesAplicadas++;
        } else {
            console.warn(">>> SALTOU: O texto local não bate com o original reportado pelo servidor. Índices desalinhados.");
        }
    });

    if (correcoesAplicadas > 0) {
        textarea.value = texto;
        analisarTexto();
        alert(`Sucesso! ${correcoesAplicadas} correções aplicadas.`);
    } else {
        alert("Não foi possível aplicar as correções. O texto pode ter sido alterado manualmente após a análise ou há um desalinhamento de índices. Tente clicar em 'Analisar' novamente antes de corrigir.");
    }
}