function toggleWidget() {
    const widget = document.getElementById('chatWidget');
    const botaoAbrir = document.getElementById('abrirChat');

    if (widget.style.display === 'flex') {
        widget.style.display = 'none';
        botaoAbrir.style.display = 'block';
    } else {
        widget.style.display = 'flex';
        botaoAbrir.style.display = 'none';
    }
}

function trocarAba(aba) {
    const duvidas = document.getElementById('conteudoDuvidas');
    const simulacao = document.getElementById('conteudoSimulacao');

    const abas = document.querySelectorAll('.aba');
    abas.forEach(a => a.classList.remove('ativa'));

    if (aba === 'duvidas') {
        duvidas.style.display = 'block';
        simulacao.style.display = 'none';
        abas[0].classList.add('ativa');
    } else {
        duvidas.style.display = 'none';
        simulacao.style.display = 'block';
        abas[1].classList.add('ativa');
        mostrarSimulador();
    }
}

function mostrarSimulador() {
    fetch('/motos')
        .then(response => response.json())
        .then(data => {
            const lista = document.getElementById('listaMotos');
            lista.innerHTML = '';
            data.forEach(moto => {
                const li = document.createElement('li');
                li.innerHTML = `
                    ${moto.nome}
                    <a href="${moto.link_simulacao}" target="_blank">
                        <button>Simular</button>
                    </a>
                `;
                lista.appendChild(li);
            });
        })
        .catch(error => {
            console.error("Erro ao carregar motos:", error);
        });
}

function enviarPergunta() {
    const pergunta = document.getElementById('perguntaInput').value;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('respostaBot').innerText = data.resposta;
    });
}
