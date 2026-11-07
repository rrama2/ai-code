(() => {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('message');
  const messages = document.getElementById('messages');
  const send = document.getElementById('send');
  const sessionId = 'web-' + (globalThis.crypto?.randomUUID?.() || Date.now().toString(36));
  function bubble(message, who, detail) {
    const el = document.createElement('article');
    el.className = 'bubble ' + who;
    el.textContent = message; // Never inject untrusted response as HTML.
    if (detail) { const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = detail; el.append(meta); }
    messages.append(el); messages.scrollTop = messages.scrollHeight;
    return el;
  }
  form.addEventListener('submit', async e => {
    e.preventDefault(); const query = input.value.trim(); if (!query || send.disabled) return;
    bubble(query, 'user'); input.value = ''; send.disabled = true;
    const pending = bubble('Checking the help center…', 'bot');
    const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), window.SUPPORT_CONFIG.timeoutMs);
    try {
      const res = await fetch(window.SUPPORT_CONFIG.endpoint, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query, customer_id: sessionId}), signal: controller.signal
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json(); pending.remove();
      if (data.status === 'answered' && data.answer) {
        bubble(data.answer, 'bot', data.source?.id ? 'Source: ' + data.source.id : 'Help center answer');
      } else if (data.status === 'escalated') {
        const id = data.ticket_id || data.escalation?.ticket_id;
        bubble(data.message || 'A support agent will review your request.', 'bot', id ? 'Ticket: ' + id : 'Ticket ID unavailable');
      } else { bubble('The support service returned an unexpected response. Please try again later.', 'bot'); }
    } catch (err) {
      pending.remove(); bubble('Unable to contact support right now. Please try again or use another support channel.', 'bot');
      console.error('Support request failed:', err);
    } finally { clearTimeout(timeout); send.disabled = false; input.focus(); }
  });
})();