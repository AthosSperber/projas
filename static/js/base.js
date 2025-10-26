// static/js/base.js - utilities
(function () {
  window.App = window.App || {};
  async function apiFetch(path, opts = {}) {
    const defaultHeaders = { 'Accept': 'application/json' };
    if (opts.body && !(opts.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(opts.body);
    }
    opts.headers = Object.assign({}, defaultHeaders, opts.headers || {});
    const res = await fetch(path, opts);
    if (!res.ok) {
      const text = await res.text().catch(()=>null);
      const err = new Error(`Request failed: ${res.status} ${res.statusText}`);
      err.status = res.status;
      err.body = text;
      throw err;
    }
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return res.json();
    }
    return res.text();
  }

  function showToast(message, category='info', timeout=5000) {
    const container = document.querySelector('.container');
    if (!container) {
      console.warn('Container for toasts not found.');
      return;
    }
    const div = document.createElement('div');
    div.className = `alert alert-${category} alert-dismissible fade show`;
    div.setAttribute('role', 'alert');
    div.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    container.prepend(div);
    if (timeout > 0) {
      setTimeout(() => {
        try { bootstrap.Alert.getOrCreateInstance(div).close(); } catch(e) {}
      }, timeout);
    }
  }

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  window.App.apiFetch = apiFetch;
  window.App.showToast = showToast;
  window.App.onReady = onReady;
})();
