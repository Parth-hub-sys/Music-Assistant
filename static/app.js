// ─── State ────────────────────────────────────────────────────
let threadId   = sessionStorage.getItem('threadId') || null;
let isLoading  = false;

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (threadId) updateSessionLabel(threadId);
  document.getElementById('userInput').focus();
});

// ─── Session ──────────────────────────────────────────────────
function updateSessionLabel(id) {
  document.getElementById('sessionLabel').textContent = 'Session: ' + id.slice(0, 8) + '...';
}

function newChat() {
  threadId = null;
  sessionStorage.removeItem('threadId');
  document.getElementById('messages').innerHTML = '';
  document.getElementById('welcome').classList.remove('hidden');
  document.getElementById('sessionLabel').textContent = 'New Session';
  document.getElementById('userInput').value = '';
  document.getElementById('userInput').style.height = 'auto';
  document.getElementById('userInput').focus();
}

// ─── Quick actions ─────────────────────────────────────────────
function quickSend(text) {
  const input = document.getElementById('userInput');
  input.value = text;
  autoResize(input);
  sendMessage();
}

// ─── Input helpers ─────────────────────────────────────────────
function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 130) + 'px';
}

function scrollToBottom() {
  const area = document.getElementById('chatArea');
  area.scrollTop = area.scrollHeight;
}

// ─── Rendering ────────────────────────────────────────────────
function hideWelcome() {
  document.getElementById('welcome').classList.add('hidden');
}

function addMessage(role, content, toolCalls) {
  const container = document.getElementById('messages');
  const msgEl = document.createElement('div');
  msgEl.className = 'message ' + role;

  // Tool badges (above bubble for assistant messages)
  if (toolCalls && toolCalls.length > 0) {
    const badgesEl = document.createElement('div');
    badgesEl.className = 'tool-badges';
    toolCalls.forEach(tc => {
      const badge = document.createElement('span');
      badge.className = 'tool-badge';
      badge.textContent = tc.name;
      badgesEl.appendChild(badge);
    });
    msgEl.appendChild(badgesEl);
  }

  const bubbleEl = document.createElement('div');
  bubbleEl.className = 'bubble';

  if (role === 'assistant') {
    // Render markdown for assistant messages
    bubbleEl.innerHTML = marked.parse(content || '');
  } else {
    bubbleEl.textContent = content || '';
  }

  msgEl.appendChild(bubbleEl);
  container.appendChild(msgEl);
  scrollToBottom();
}

function showTyping() {
  const container = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'typing-wrap';
  el.id = 'typing-indicator';
  el.innerHTML = `
    <div class="typing-bubble">
      <div class="dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <span class="typing-label">Processing…</span>
    </div>`;
  container.appendChild(el);
  scrollToBottom();
}

function hideTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ─── Send ──────────────────────────────────────────────────────
async function sendMessage() {
  if (isLoading) return;

  const input   = document.getElementById('userInput');
  const message = input.value.trim();
  if (!message) return;

  // Clear input immediately
  input.value = '';
  input.style.height = 'auto';

  hideWelcome();
  addMessage('user', message, []);

  isLoading = true;
  document.getElementById('sendBtn').disabled = true;
  showTyping();

  try {
    const resp = await fetch('/api/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message, thread_id: threadId }),
    });

    const data = await resp.json();
    hideTyping();

    // Persist thread id
    if (data.thread_id) {
      threadId = data.thread_id;
      sessionStorage.setItem('threadId', threadId);
      updateSessionLabel(threadId);
    }

    if (data.success) {
      addMessage('assistant', data.content, data.tool_calls || []);
    } else {
      addMessage('error', data.content || 'An unexpected error occurred.', []);
    }

  } catch (err) {
    hideTyping();
    addMessage('error', 'Network error: ' + err.message, []);
  } finally {
    isLoading = false;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
  }
}
