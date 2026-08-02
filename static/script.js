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

// ================================
// Phase 10 Step 6 - Live Charts
// ================================


const body = document.querySelector("body");


if(body.dataset.amounts){


    const amounts = JSON.parse(
        body.dataset.amounts
    );


    const statuses = JSON.parse(
        body.dataset.statuses
    );


    const riskPoints = JSON.parse(
        body.dataset.risk
    );



    // -------------------------
    // Spending Chart
    // -------------------------

    new Chart(
        document.getElementById("spendingChart"),
        {

            type: "line",

            data: {

                labels: amounts.map(
                    (_,i)=>"TX "+(i+1)
                ),

                datasets:[{

                    label:"Amount Spent",

                    data: amounts,

                    borderWidth:2

                }]

            }

        }

    );



    // -------------------------
    // Transaction Activity Chart
    // -------------------------

    let approved = statuses.filter(
        s=>s==="Approved"
    ).length;


    let blocked = statuses.filter(
        s=>s==="Blocked"
    ).length;


    let pending = statuses.filter(
        s=>s==="Pending Approval"
    ).length;



    new Chart(
        document.getElementById("transactionChart"),
        {

            type:"bar",

            data:{

                labels:[
                    "Approved",
                    "Blocked",
                    "Pending"
                ],

                datasets:[{

                    label:"Transactions",

                    data:[
                        approved,
                        blocked,
                        pending
                    ],

                    borderWidth:1

                }]

            }

        }

    );



    // -------------------------
    // Risk Chart
    // -------------------------

    new Chart(
        document.getElementById("riskChart"),
        {

            type:"line",

            data:{

                labels:riskPoints.map(
                    (_,i)=>"Check "+(i+1)
                ),

                datasets:[{

                    label:"Risk Score",

                    data:riskPoints,

                    borderWidth:2

                }]

            }

        }

    );


}

// =====================================
// Phase 10 Step 7
// Live Transaction Monitoring
// =====================================


function loadLiveTransactions(){


fetch("/api/live-transactions")

.then(response=>response.json())


.then(data=>{


let container =
document.getElementById(
"liveTransactions"
);



if(!container)
return;



container.innerHTML="";



data.forEach(tx=>{


let statusClass="pending";


if(tx.status==="Approved")
{
statusClass="success";
}


else if(tx.status==="Blocked")
{
statusClass="danger";
}



container.innerHTML += `


<div class="monitor-row">


<span>
${new Date().toLocaleTimeString()}
</span>


<strong>
${tx.merchant}
</strong>


<span>
₹${tx.amount}
</span>


<em class="${statusClass}">
${tx.status}
</em>


</div>


`;


});


});


}



// Initial load

loadLiveTransactions();



// Refresh every 3 seconds

setInterval(
loadLiveTransactions,
3000
);

// ======================================
// REPORT PAGE CHARTS
// ======================================

if (window.location.pathname === "/reports") {

    const body = document.body;

    const trend = JSON.parse(body.dataset.trend || "[]");

    const categoryLabels = JSON.parse(body.dataset.categoryLabels || "[]");

    const categoryValues = JSON.parse(body.dataset.categoryValues || "[]");


    // ----------------------------
    // Spending Trend
    // ----------------------------

    const trendCanvas = document.getElementById("spendingTrendChart");

    if (trendCanvas) {

        new Chart(trendCanvas, {

            type: "line",

            data: {

                labels: trend.map((_, i) => "T" + (i + 1)),

                datasets: [{

                    label: "Spend",

                    data: trend,

                    borderWidth: 3,

                    tension: 0.4,

                    fill: true

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false

            }

        });

    }


    // ----------------------------
    // Category Chart
    // ----------------------------

    const categoryCanvas = document.getElementById("categoryChart");

    if (categoryCanvas) {

        new Chart(categoryCanvas, {

            type: "doughnut",

            data: {

                labels: categoryLabels,

                datasets: [{

                    data: categoryValues

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false

            }

        });

    }

}
// ======================================
// EXPORT REPORT PDF
// ======================================

const exportBtn = document.getElementById("exportPdfBtn");

if (exportBtn) {

    exportBtn.addEventListener("click", () => {

        const trendCanvas = document.getElementById("spendingTrendChart");
        const pieCanvas = document.getElementById("categoryChart");

        if (!trendCanvas || !pieCanvas) {
            alert("Charts not found!");
            return;
        }

        const trendImage = trendCanvas.toDataURL("image/png");
        const pieImage = pieCanvas.toDataURL("image/png");

        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/export-pdf";

        const trendInput = document.createElement("input");
        trendInput.type = "hidden";
        trendInput.name = "trend";
        trendInput.value = trendImage;

        const pieInput = document.createElement("input");
        pieInput.type = "hidden";
        pieInput.name = "pie";
        pieInput.value = pieImage;

        form.appendChild(trendInput);
        form.appendChild(pieInput);

        document.body.appendChild(form);
        form.submit();

    });

}