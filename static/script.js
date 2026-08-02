document.querySelectorAll('.toggle-password').forEach((button) => {
  button.addEventListener('click', () => {
    const input = button.parentElement.querySelector('input');
    input.type = input.type === 'password' ? 'text' : 'password';
    button.textContent = input.type === 'password' ? '?' : '?';
  });
});

document.querySelectorAll('[data-demo-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const username = form.querySelector('[name="username"]')?.value.trim();
    if (username) localStorage.setItem('killSwitchUsername', username);
    window.location.href = '/dashboard';
  });
});

document.querySelectorAll('[data-agent-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;

    const agentName = form.querySelector('input[type="text"]')?.value.trim();
    const agents = JSON.parse(localStorage.getItem('killSwitchAgents') || '[]');
    if (agentName && !agents.includes(agentName)) {
      agents.push(agentName);
      localStorage.setItem('killSwitchAgents', JSON.stringify(agents));
    }

    const toast = document.querySelector('.toast');
    toast?.classList.add('show');
    setTimeout(() => (window.location.href = '/tasks'), 900);
  });
});

const agentGrid = document.querySelector('[data-agent-task-grid]');
if (agentGrid) {
  const agents = JSON.parse(localStorage.getItem('killSwitchAgents') || '[]');
  const emptyState = document.querySelector('[data-empty-agents]');
  emptyState.style.display = agents.length ? 'none' : 'block';
  agentGrid.innerHTML = agents.map((agent) => `<article class="agent-task-card"><div class="agent-card-mark">✦</div><h2>${agent}</h2><p>Ready for a new protected mission.</p><a href="/assign-task?agent=${encodeURIComponent(agent)}">Assign Task →</a></article>`).join('');
}

const taskAgentName = document.querySelector('[data-agent-name]');
if (taskAgentName) {
  const agent = new URLSearchParams(window.location.search).get('agent');
  taskAgentName.textContent = agent || 'AI Agent';
}

document.querySelectorAll('[data-task-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const toast = document.querySelector('.toast');
    toast?.classList.add('show');
    setTimeout(() => (window.location.href = '/tasks'), 1000);
  });
});

// Several dashboard templates share placeholder navigation links. Route those
// entries to their functional pages until all layouts are consolidated.
const dashboardRoutes = {
  'Wallets': '/wallets',
  'Transactions': '/transactions',
  'Security Policies': '/security-policies',
  'Monitoring': '/monitoring',
  'Alerts': '/alerts',
  'Reports': '/reports'
};
document.querySelectorAll('.dashboard-nav a').forEach((link) => {
  const label = Object.keys(dashboardRoutes).find((name) =>
    link.textContent.includes(name)
  );
  const destination = label ? dashboardRoutes[label] : undefined;
  if (destination && link.getAttribute('href') === '#') link.href = destination;
});

const savedUsername = localStorage.getItem('killSwitchUsername');
if (savedUsername) {
  document.querySelectorAll('.topbar-actions strong').forEach((name) => {
    name.textContent = savedUsername;
  });
  document.querySelectorAll('.account-avatar').forEach((avatar) => {
    avatar.textContent = savedUsername.charAt(0).toUpperCase();
  });
}

document.querySelectorAll('.dashboard-nav a').forEach((link) => {
  if (!link.textContent.includes('Settings')) return;
  link.href = '/login';
  link.innerHTML = '<i>⇥</i>Logout';
  link.addEventListener('click', () => {
    localStorage.removeItem('killSwitchUsername');
  });
});

document.querySelectorAll('.notification-button').forEach((button) => button.remove());

if (document.body.classList.contains('dashboard-body')) {
  const chat = document.createElement('section');
  chat.className = 'chatbot';
  chat.innerHTML = `
    <button class="chatbot-launch" type="button" aria-label="Open assistant">🤖</button>
    <div class="chatbot-panel" hidden>
      <header><span>🤖</span><div><strong>Kill Switch Assistant</strong><small>Security help</small></div><button type="button" aria-label="Close assistant">×</button></header>
      <div class="chatbot-messages"><p class="chatbot-message assistant">Hi! How can I help protect your agent today?</p></div>
      <form class="chatbot-form"><input aria-label="Message assistant" maxlength="2000" placeholder="Ask about security..." required><button type="submit">Send</button></form>
    </div>`;
  document.body.append(chat);
  const launch = chat.querySelector('.chatbot-launch');
  const panel = chat.querySelector('.chatbot-panel');
  const close = chat.querySelector('header button');
  const form = chat.querySelector('.chatbot-form');
  const input = form.querySelector('input');
  const messages = chat.querySelector('.chatbot-messages');
  const history = [];
  launch.addEventListener('click', () => { panel.hidden = !panel.hidden; if (!panel.hidden) input.focus(); });
  close.addEventListener('click', () => { panel.hidden = true; });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const content = input.value.trim();
    if (!content) return;
    history.push({ role: 'user', content });
    messages.insertAdjacentHTML('beforeend', `<p class="chatbot-message user"></p>`);
    messages.lastElementChild.textContent = content;
    input.value = '';
    const waiting = document.createElement('p');
    waiting.className = 'chatbot-message assistant';
    waiting.textContent = 'Thinking…';
    messages.append(waiting); messages.scrollTop = messages.scrollHeight;
    try {
      const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(history) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error);
      waiting.textContent = data.reply;
      history.push({ role: 'assistant', content: data.reply });
    } catch (error) { waiting.textContent = error.message || 'Unable to reach the assistant.'; }
    messages.scrollTop = messages.scrollHeight;
  });
}

document.querySelectorAll('.google-button').forEach((button) => {
  button.addEventListener('click', () => { window.location.href = '/auth/google'; });
});
document.querySelectorAll('.or-divider').forEach((divider) => {
  divider.textContent = 'Continue with Google';
});
/* ==========================
   TASK MODAL
========================== */

function openTaskModal(){

    const modal = document.getElementById("taskModal");

    if(modal){
        modal.style.display = "flex";
    }

}

function closeTaskModal(){

    const modal = document.getElementById("taskModal");

    if(modal){
        modal.style.display = "none";
    }

}

/* Close when clicking outside */

window.onclick = function(event){

    const modal = document.getElementById("taskModal");

    if(modal && event.target === modal){

        closeTaskModal();

    }

};

/* Close on ESC */

document.addEventListener("keydown", function(e){

    if(e.key === "Escape"){

        closeTaskModal();

    }

});

/* Auto hide flash messages */

setTimeout(function(){

    const flashes = document.querySelectorAll(".flash-message");

    flashes.forEach(function(msg){

        msg.style.transition = "0.5s";
        msg.style.opacity = "0";

        setTimeout(function(){

            msg.remove();

        },500);

    });

},3000);

function openTransactionModal() {

    document.getElementById("transactionModal").style.display = "flex";

}

function closeTransactionModal() {

    document.getElementById("transactionModal").style.display = "none";

}

window.onclick = function(event) {

    const modal = document.getElementById("transactionModal");

    if (event.target == modal) {

        modal.style.display = "none";

    }

}

function openPolicyModal() {
    document.getElementById("policyModal").style.display = "flex";
}

function closePolicyModal() {
    document.getElementById("policyModal").style.display = "none";
}