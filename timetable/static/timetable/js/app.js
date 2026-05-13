/* ─── CSRF helper ─── */
function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

function getCsrfToken() {
  // Try cookie first
  let token = getCookie('csrftoken');
  // If not found, try meta tag
  if (!token) {
    const meta = document.querySelector('meta[name="csrf-token"]');
    token = meta ? meta.getAttribute('content') : null;
  }
  return token;
}

/* ─── Toast notifications ─── */
function toast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  el.innerHTML = `<span style="font-size:1.1rem">${icons[type] || 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

/* ─── API fetch helper ─── */
async function api(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
  };
  const res = await fetch(url, { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
  return data;
}

/* ─── Modal helpers ─── */
function openModal(id) {
  document.getElementById(id)?.classList.add('open');
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
});

// Close modal buttons
document.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
  btn.addEventListener('click', () => {
    const modal = btn.closest('.modal-backdrop');
    if (modal) modal.classList.remove('open');
  });
});

/* ─── Color picker preview ─── */
document.querySelectorAll('input[type=color]').forEach(input => {
  const preview = input.closest('.form-group')?.querySelector('.color-preview');
  if (preview) {
    preview.style.background = input.value;
    input.addEventListener('input', () => { preview.style.background = input.value; });
  }
});

/* ─── Day picker ─── */
function initDayPicker(containerId, inputId) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  if (!container || !input) return;

  const days = [
    { value: 1, label: 'Mon' }, { value: 2, label: 'Tue' },
    { value: 3, label: 'Wed' }, { value: 4, label: 'Thu' },
    { value: 5, label: 'Fri' },
  ];
  let selected = JSON.parse(input.value || '[1,2,3,4,5]');

  function render() {
    container.innerHTML = '';
    days.forEach(d => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'day-btn' + (selected.includes(d.value) ? ' selected' : '');
      btn.textContent = d.label;
      btn.onclick = () => {
        if (selected.includes(d.value)) {
          selected = selected.filter(v => v !== d.value);
        } else {
          selected = [...selected, d.value].sort();
        }
        input.value = JSON.stringify(selected);
        render();
      };
      container.appendChild(btn);
    });
  }
  render();
}

/* ─── Search filter ─── */
function initSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}

/* ─── Confirm delete ─── */
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this item?');
}

/* ─── Loading button state ─── */
function setLoading(btn, loading) {
  if (loading) {
    btn._originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span>';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._originalHTML || btn.innerHTML;
    btn.disabled = false;
  }
}
