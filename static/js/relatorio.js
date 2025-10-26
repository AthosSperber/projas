// static/js/relatorio.js
(function () {
  async function fetchRelatorio() {
    try {
      const res = await fetch('/api/relatorio-data');
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      console.error('Erro fetch relatorio:', e);
      return null;
    }
  }

  function buildSummary(items) {
    const summary = {};
    items.forEach(it => {
      const s = it.Sentimento || it.sentiment || 'neutro';
      summary[s] = (summary[s] || 0) + 1;
    });
    return summary;
  }

  function updateChart(labels, values) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    if (window._pieChart) window._pieChart.destroy();
    window._pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels,
        datasets: [{ data: values }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }

  function populateTable(items) {
    const tbody = document.querySelector('#table-details tbody');
    tbody.innerHTML = '';
    items.forEach(it => {
      const tr = document.createElement('tr');
      const tdText = document.createElement('td'); tdText.innerText = it.texto || it.Quote || '';
      const tdSent = document.createElement('td'); tdSent.innerText = it.Sentimento || it.sentiment || '';
      const tdConf = document.createElement('td'); tdConf.innerText = (it.Confianca !== undefined) ? String(it.Confianca).slice(0,6) : '';
      tr.appendChild(tdText); tr.appendChild(tdSent); tr.appendChild(tdConf);
      tbody.appendChild(tr);
    });
  }

  async function loadDataToUI() {
    const data = await fetchRelatorio();
    if (!data) {
      document.getElementById('summaryList').innerHTML = '<li>Nenhum relatório disponível. Clique em "Rodar análise agora".</li>';
      return;
    }
    const items = data.items || [];
    const summary = buildSummary(items);
    const labels = Object.keys(summary);
    const values = labels.map(l => summary[l]);

    const ul = document.getElementById('summaryList');
    ul.innerHTML = '';
    const total = items.length || 1;
    labels.forEach(k => {
      const li = document.createElement('li');
      li.innerText = `${k}: ${summary[k]} (${((summary[k]/total)*100).toFixed(2)}%)`;
      ul.appendChild(li);
    });

    updateChart(labels, values);
    populateTable(items);
    // show results container
    document.getElementById('results').style.display = 'block';
  }

  App.onReady(() => {
    const btnRun = document.getElementById('btn-run');
    if (btnRun) {
      btnRun.addEventListener('click', async () => {
        btnRun.disabled = true;
        btnRun.innerText = 'Executando...';
        document.getElementById('loading').style.display = 'block';
        try {
          const res = await fetch('/admin/run-analysis', { method: 'POST' });
          if (!res.ok) {
            const text = await res.text().catch(()=>null);
            App.showToast('Erro ao executar análise: ' + (text || res.statusText), 'danger');
            console.error('run-analysis erro', res.status, text);
            btnRun.disabled = false;
            btnRun.innerText = 'Rodar análise agora';
            document.getElementById('loading').style.display = 'none';
            return;
          }
          const data = await res.json().catch(()=>null);
          if (data && (data.json || data.pdf)) {
            App.showToast('Análise concluída.', 'success');
          } else {
            App.showToast('Análise concluída (sem artefatos detectados).', 'warning');
          }
          await loadDataToUI();
        } catch (e) {
          console.error(e);
          App.showToast('Falha executando análise (ver logs).', 'danger');
        } finally {
          if (btnRun) {
            btnRun.disabled = false;
            btnRun.innerText = 'Rodar análise agora';
          }
          document.getElementById('loading').style.display = 'none';
        }
      });
    }

    // Email send
    const sendEmailBtn = document.getElementById('sendEmailBtn');
    const emailInput = document.getElementById('emailInput');
    const emailStatus = document.getElementById('emailStatus');
    if (sendEmailBtn) {
      sendEmailBtn.addEventListener('click', async () => {
        const email = emailInput.value.trim();
        if (!email) {
          App.showToast('Digite um e-mail válido!', 'warning');
          return;
        }
        sendEmailBtn.disabled = true;
        emailStatus.textContent = 'Enviando relatório...';
        try {
          const res = await fetch('/send-report-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
          });
          const data = await res.json().catch(()=>null);
          if (res.ok && data && data.success) {
            App.showToast(`Relatório enviado para ${email}!`, 'success');
            emailStatus.textContent = `✅ Enviado para ${email}`;
          } else {
            App.showToast(data && data.error ? data.error : 'Erro ao enviar relatório.', 'danger');
            emailStatus.textContent = '❌ Erro ao enviar.';
          }
        } catch (e) {
          console.error('send email error', e);
          App.showToast('Falha ao enviar o relatório.', 'danger');
          emailStatus.textContent = '❌ Erro de rede.';
        } finally {
          sendEmailBtn.disabled = false;
        }
      });
    }

    // initial load: try to load existing report if any
    loadDataToUI();
  });
})();
