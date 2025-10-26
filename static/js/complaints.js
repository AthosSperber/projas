// static/js/complaints.js
(function () {
  App.onReady(() => {
    const table = document.getElementById('complaintsTable');
    const filterInput = document.getElementById('filterInput');
    const btnExport = document.getElementById('btnExportCSV');
    if (!table) return;
    if (filterInput) {
      filterInput.addEventListener('input', () => {
        const q = filterInput.value.trim().toLowerCase();
        const trs = table.querySelectorAll('tbody tr');
        trs.forEach(tr => {
          const text = tr.innerText.toLowerCase();
          tr.style.display = text.includes(q) ? '' : 'none';
        });
      });
    }
    if (btnExport) {
      btnExport.addEventListener('click', () => {
        const rows = Array.from(table.querySelectorAll('tr')).map(tr =>
          Array.from(tr.querySelectorAll('th,td')).map(td => `"${(td.innerText || '').replace(/"/g, '""')}"`).join(',')
        ).join('\n');
        const blob = new Blob([rows], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reclamacoes_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      });
    }
  });
})();
