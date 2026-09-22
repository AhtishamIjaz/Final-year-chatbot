/* ═══════════════════════════════════════════════════════════════
   MedGPT — app.js
   Frontend logic: Chat, Appointments, Tab switching
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin.includes('http') ? window.location.origin : 'http://localhost:8000';

/* ── State ─────────────────────────────────────────────────────── */
let chatHistory = [];
let isBusy      = false;

/* ════════════════════════════════════════════════════════════════
   TAB SWITCHING
   ════════════════════════════════════════════════════════════════ */
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`tab-${name}`).classList.add('active');
  document.querySelector(`[data-tab="${name}"]`).classList.add('active');
  if (name === 'appointments') loadAppointments();
}

/* ════════════════════════════════════════════════════════════════
   CHAT
   ════════════════════════════════════════════════════════════════ */

/** Send from quick-chip button */
function quickSend(text) {
  const input = document.getElementById('userInput');
  input.value = text;
  autoResize(input);
  sendMessage();
}

/** Keyboard handler — Enter = send, Shift+Enter = newline */
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

/** Auto-grow textarea */
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

/** Main send function */
async function sendMessage() {
  if (isBusy) return;

  const input   = document.getElementById('userInput');
  const text    = input.value.trim();
  if (!text) return;

  // Clear input
  input.value = '';
  input.style.height = 'auto';

  // Append user bubble
  appendMessage('user', text);
  chatHistory.push({ role: 'user', content: text });

  // Lock UI
  isBusy = true;
  document.getElementById('sendBtn').disabled = true;
  showTyping(true);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: chatHistory.slice(-12) }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Server error' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    showTyping(false);

    appendMessage('ai', data.response, data.sources || []);
    chatHistory.push({ role: 'assistant', content: data.response });

  } catch (err) {
    showTyping(false);
    appendMessage('ai',
      `⚠️ **Connection Error**\n\nCould not reach the MedGPT server. Please make sure the backend is running.\n\n` +
      `**Error:** ${err.message}\n\n` +
      `**To start the server:** Open a terminal in the \`backend/\` folder and run:\n\`uvicorn main:app --reload\``,
      []);
    showToast('Cannot connect to server. Is the backend running?', 'error');
  } finally {
    isBusy = false;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
  }
}

/* ── Render helpers ────────────────────────────────────────────── */

function appendMessage(role, text, sources = []) {
  const container = document.getElementById('chatMessages');

  const wrapper = document.createElement('div');
  wrapper.className = `msg ${role === 'ai' ? 'ai-msg' : 'user-msg'}`;

  const avatar = document.createElement('div');
  avatar.className = `msg-avatar ${role === 'ai' ? 'ai-av' : 'user-av'}`;
  avatar.innerHTML = role === 'ai'
    ? '<i class="fas fa-robot"></i>'
    : '<i class="fas fa-user"></i>';

  const body = document.createElement('div');
  body.className = 'msg-body';

  // Bubble
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = formatMarkdown(text);
  body.appendChild(bubble);

  // Meta row
  const meta = document.createElement('div');
  meta.className = 'msg-meta';

  const timeEl = document.createElement('span');
  timeEl.className = 'msg-time';
  timeEl.textContent = formatTime(new Date());
  meta.appendChild(timeEl);

  if (role === 'ai') {
    const badge = document.createElement('span');
    badge.className = 'rag-badge';
    badge.innerHTML = '<i class="fas fa-shield-alt"></i> RAG-Powered';
    meta.appendChild(badge);
  }

  body.appendChild(meta);

  // Sources
  if (sources && sources.length > 0) {
    const srcRow = document.createElement('div');
    srcRow.className = 'sources-row';

    const lbl = document.createElement('span');
    lbl.className = 'sources-label';
    lbl.innerHTML = '<i class="fas fa-book-open"></i> Sources:';
    srcRow.appendChild(lbl);

    sources.forEach(src => {
      const pill = document.createElement('span');
      pill.className = 'source-pill';
      pill.innerHTML = `<i class="fas fa-file-medical"></i> ${src.replace('.txt', '')}`;
      srcRow.appendChild(pill);
    });

    body.appendChild(srcRow);
  }

  wrapper.appendChild(avatar);
  wrapper.appendChild(body);
  container.appendChild(wrapper);
  scrollToBottom();
}

/** Very lightweight markdown → HTML converter */
function formatMarkdown(text) {
  return text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9;padding:1px 5px;border-radius:3px;font-size:.9em">$1</code>')
    // H3
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    // H4
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    // Bullet list items
    .replace(/^[•\-\*] (.+)$/gm, '<li>$1</li>')
    // Numbered list items
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/(<li>[\s\S]*?<\/li>)(\n<li>[\s\S]*?<\/li>)*/g, m => `<ul>${m}</ul>`)
    // Double newline → paragraph break
    .replace(/\n{2,}/g, '</p><p>')
    // Single newline → <br>
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(.+)/, '<p>$1')
    .replace(/(.+)$/, '$1</p>')
    // Fix nested <p> inside tags
    .replace(/<p><\/p>/g, '');
}

function formatTime(d) {
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  const c = document.getElementById('chatMessages');
  c.scrollTo({ top: c.scrollHeight, behavior: 'smooth' });
}

function showTyping(visible) {
  document.getElementById('typingIndicator').style.display = visible ? 'flex' : 'none';
  if (visible) scrollToBottom();
}

/* ════════════════════════════════════════════════════════════════
   APPOINTMENTS
   ════════════════════════════════════════════════════════════════ */

async function bookAppointment(e) {
  e.preventDefault();

  const payload = {
    patient_name: document.getElementById('patientName').value.trim(),
    phone:        document.getElementById('patientPhone').value.trim(),
    doctor:       document.getElementById('doctorSelect').value,
    date:         document.getElementById('apptDate').value,
    time:         document.getElementById('apptTime').value,
    reason:       document.getElementById('visitReason').value.trim(),
  };

  try {
    const res = await fetch(`${API_BASE}/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Booking failed');

    const data = await res.json();
    document.getElementById('apptForm').reset();
    showModal(
      `Your appointment with <strong>${payload.doctor}</strong> has been confirmed for ` +
      `<strong>${formatDate(payload.date)}</strong> at <strong>${payload.time}</strong>.<br><br>` +
      `A confirmation has been saved to your appointments list.`
    );
    loadAppointments();
    showToast('Appointment booked successfully!', 'success');

  } catch {
    showToast('Could not book appointment. Is the server running?', 'error');
  }
}

async function loadAppointments() {
  const list = document.getElementById('apptList');
  list.innerHTML = '<div class="empty-state"><i class="fas fa-spinner fa-spin"></i><p>Loading…</p></div>';

  try {
    const res = await fetch(`${API_BASE}/appointments`);
    if (!res.ok) throw new Error();
    const appts = await res.json();

    if (!appts.length) {
      list.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-calendar-times"></i>
          <p>No appointments yet</p>
          <span>Book your first appointment using the form</span>
        </div>`;
      return;
    }

    list.innerHTML = '';
    appts.forEach(a => list.appendChild(buildApptCard(a)));

  } catch {
    list.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-exclamation-triangle" style="color:var(--warning)"></i>
        <p>Could not load appointments</p>
        <span>Make sure the backend server is running</span>
      </div>`;
  }
}

function buildApptCard(a) {
  const div = document.createElement('div');
  div.className = `appt-item ${a.status === 'cancelled' ? 'cancelled' : ''}`;
  div.id = `appt-${a.id}`;

  div.innerHTML = `
    <div class="appt-header">
      <div class="appt-name"><i class="fas fa-user" style="margin-right:6px;color:var(--primary-light)"></i>${a.patient_name}</div>
      <div class="appt-status ${a.status}">${a.status === 'confirmed' ? '✓ Confirmed' : '✕ Cancelled'}</div>
    </div>
    <div class="appt-detail"><i class="fas fa-user-md"></i>${a.doctor}</div>
    <div class="appt-detail"><i class="fas fa-calendar"></i>${formatDate(a.date)} &nbsp;·&nbsp; ${a.time}</div>
    <div class="appt-detail"><i class="fas fa-notes-medical"></i>${a.reason}</div>
    ${a.phone ? `<div class="appt-detail"><i class="fas fa-phone"></i>${a.phone}</div>` : ''}
    ${a.status === 'confirmed' ? `
      <div class="appt-actions">
        <button class="btn-cancel" onclick="cancelAppt('${a.id}')">
          <i class="fas fa-times-circle"></i> Cancel Appointment
        </button>
      </div>` : ''}
  `;

  return div;
}

async function cancelAppt(id) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return;

  try {
    const res = await fetch(`${API_BASE}/appointments/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    showToast('Appointment cancelled.', 'info');
    loadAppointments();
  } catch {
    showToast('Could not cancel. Please try again.', 'error');
  }
}

/* ════════════════════════════════════════════════════════════════
   HELPERS
   ════════════════════════════════════════════════════════════════ */

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-PK', {
      weekday: 'short', year: 'numeric', month: 'long', day: 'numeric'
    });
  } catch { return dateStr; }
}

let toastTimer;
function showToast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className   = `toast show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3500);
}

function showModal(msg) {
  document.getElementById('modalMsg').innerHTML = msg;
  document.getElementById('modal').style.display = 'flex';
}

function closeModal(e) {
  if (e.target.id === 'modal') document.getElementById('modal').style.display = 'none';
}

function closeModalBtn() {
  document.getElementById('modal').style.display = 'none';
}

/* ════════════════════════════════════════════════════════════════
   INIT
   ════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  // Set minimum date for appointment booking to today
  const dateInput = document.getElementById('apptDate');
  if (dateInput) {
    dateInput.min = new Date().toISOString().split('T')[0];
  }
  // Focus chat input
  document.getElementById('userInput')?.focus();
});
