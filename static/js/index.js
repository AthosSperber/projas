// static/js/index.js
(function () {
  App.onReady(() => {
    const form = document.getElementById('meuForm');
    const btn = form ? form.querySelector('button[type="submit"]') : null;
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (btn) {
        btn.disabled = true;
        btn.dataset.orig = btn.innerText;
        btn.innerText = 'Enviando...';
      }
      const formData = new FormData(form);
      try {
        const res = await fetch('/submit', {
          method: 'POST',
          body: formData
        });
        if (res.redirected) {
          window.location.href = res.url;
          return;
        }
        if (!res.ok) {
          const text = await res.text();
          App.showToast('Erro ao enviar formulário: ' + res.statusText, 'danger');
          console.error('submit error', res.status, text);
          return;
        }
        App.showToast('Enviado com sucesso!', 'success');
        form.reset();
        const header = document.querySelector('.main-header');
        const top = header ? header.offsetHeight + 10 : 0;
        window.scrollTo({ top, behavior: 'smooth' });
      } catch (err) {
        console.error(err);
        App.showToast('Erro de rede ao enviar formulário.', 'danger');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerText = btn.dataset.orig || 'Enviar';
        }
      }
    });
  });
})();
