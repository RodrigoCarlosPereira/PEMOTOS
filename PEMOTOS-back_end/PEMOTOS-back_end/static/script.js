const chatToggle = document.getElementById('chat-toggle');
const chatContainer = document.getElementById('chat-container');
const chatMinimize = document.getElementById('chat-minimize');
const chatClose = document.getElementById('chat-close');
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

// Abrir chat
chatToggle.addEventListener('click', () => {
  chatContainer.style.display = 'flex';
  chatToggle.style.display = 'none';
  chatInput.focus();

  // Adiciona a mensagem inicial do bot
  if (!chatMessages.hasChildNodes()) {
    addBotMessage('Olá! Seja bem-vindo(a) à PE Motos. Como podemos ajudar você hoje?');
  }
});

// Minimizar chat 
chatMinimize.addEventListener('click', () => {
  chatContainer.style.display = 'none';
  chatToggle.style.display = 'flex';
});

// Fechar chat 
chatClose.addEventListener('click', () => {
  chatContainer.style.display = 'none';
  chatToggle.style.display = 'flex';
  chatMessages.innerHTML = '';
});

// Adiciona mensagem do usuário no chat
function addUserMessage(text) {
  const msg = document.createElement('div');
  msg.classList.add('message', 'user');
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Adiciona mensagem do bot no chat
function addBotMessage(text) {
  const msg = document.createElement('div');
  msg.classList.add('message', 'bot');
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enviar mensagem (integrar a API)
chatForm.addEventListener('submit', e => {
  e.preventDefault();
  const userText = chatInput.value.trim();
  if (!userText) return;
  addUserMessage(userText);
  chatInput.value = '';
  chatInput.focus();

  // Fazer a chamada para API e ao receber resposta:
  // addBotMessage(respostaDaApi);
});

// Abrir chat com teclado (acessibilidade)
chatToggle.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    chatToggle.click();
  }
});
