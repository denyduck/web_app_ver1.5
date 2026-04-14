/*
  prohlizet.js
  - Načte soubory z /prohlizet/data (JSON)
  - Živé filtrování podle názvu + obsahu
  - Řazení A→Z / Z→A
  - Stránkování s volbou počtu položek (12 / 24 / 48 / Vše)
  - Otevření PDF v modalu
*/

let itemsPerPage  = 24;

let allFiles      = [];
let filteredFiles = [];
let currentPage   = 1;

// ── Pomocné funkce ────────────────────────────────────────────────

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function buildPdfPath(file) {
  const dir = file.directory ? file.directory.replace(/^\/+|\/+$/g, '') + '/' : '';
  return `/pdfs/${dir}${file.filename}`;
}

// ── Filtrování + řazení ───────────────────────────────────────────

function applyFiltersAndSort() {
  const query = document.getElementById('searchInput').value.trim().toLowerCase();
  const sort  = document.getElementById('sortSelect').value;

  // zobraz / skryj tlačítko clear
  document.getElementById('clearSearch').style.display = query ? 'inline-flex' : 'none';

  filteredFiles = allFiles.filter(f =>
    f.filename.toLowerCase().includes(query) ||
    (f.kontent && f.kontent.toLowerCase().includes(query))
  );

  filteredFiles.sort((a, b) =>
    sort === 'az'
      ? a.filename.localeCompare(b.filename, 'cs')
      : b.filename.localeCompare(a.filename, 'cs')
  );

  currentPage = 1;
  render();
}

// ── Vykreslení karet ──────────────────────────────────────────────

function render() {
  const grid      = document.getElementById('fileGrid');
  const countEl   = document.getElementById('fileCount');
  const total     = filteredFiles.length;
  const pageSize  = itemsPerPage === 0 ? total : itemsPerPage;
  const start     = (currentPage - 1) * pageSize;
  const pageFiles = itemsPerPage === 0 ? filteredFiles : filteredFiles.slice(start, start + pageSize);

  countEl.textContent = `${total} ${total === 1 ? 'soubor' : total < 5 ? 'soubory' : 'souborů'}`;

  if (total === 0) {
    grid.innerHTML = `
      <div class="col-12 text-center text-muted py-5">
        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
        Žádné soubory nenalezeny.
      </div>`;
    renderPagination(0);
    return;
  }

  grid.innerHTML = pageFiles.map(file => {
    const pdfPath = buildPdfPath(file);
    const dir     = file.directory || '';
    const kontent = file.kontent   || 'Bez obsahu';

    return `
      <div class="col">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body d-flex gap-3">
            <i class="bi bi-file-earmark-pdf fs-2 text-danger flex-shrink-0 mt-1"></i>
            <div class="overflow-hidden">
              <h6 class="card-title text-truncate mb-1" title="${escHtml(file.filename)}">
                ${escHtml(file.filename)}
              </h6>
              <p class="card-text text-muted small mb-0 lh-sm file-preview">
                ${escHtml(kontent)}
              </p>
            </div>
          </div>
          <div class="card-footer bg-transparent border-0 d-flex justify-content-between align-items-center pt-0">
            ${dir
              ? `<span class="badge text-bg-secondary text-truncate" style="max-width:150px"
                       title="${escHtml(dir)}">
                   <i class="bi bi-folder2-open me-1"></i>${escHtml(dir)}
                 </span>`
              : '<span></span>'}
            <button class="btn btn-sm btn-primary open-pdf-btn"
                    data-path="${escHtml(pdfPath)}"
                    data-filename="${escHtml(file.filename)}">
              <i class="bi bi-eye me-1"></i>Náhled
            </button>
          </div>
        </div>
      </div>`;
  }).join('');

  // napojení event listenerů na tlačítka
  grid.querySelectorAll('.open-pdf-btn').forEach(btn => {
    btn.addEventListener('click', () =>
      openPdfModal(btn.dataset.path, btn.dataset.filename)
    );
  });

  renderPagination(total);
}

// ── Stránkování ───────────────────────────────────────────────────

function renderPagination(total) {
  const container  = document.getElementById('paginationContainer');

  if (itemsPerPage === 0) { container.innerHTML = ''; return; }

  const totalPages = Math.ceil(total / itemsPerPage);

  if (totalPages <= 1) { container.innerHTML = ''; return; }

  const delta = 2;
  const range = [];
  for (let i = Math.max(1, currentPage - delta); i <= Math.min(totalPages, currentPage + delta); i++) {
    range.push(i);
  }

  const items = [
    li(currentPage === 1, `<i class="bi bi-chevron-left"></i>`, currentPage - 1),
    ...(range[0] > 1 ? [`<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`] : []),
    ...range.map(p => li(false, p, p, p === currentPage)),
    ...(range.at(-1) < totalPages ? [`<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`] : []),
    li(currentPage === totalPages, `<i class="bi bi-chevron-right"></i>`, currentPage + 1),
  ];

  container.innerHTML = `<ul class="pagination">${items.join('')}</ul>`;

  container.querySelectorAll('button[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = parseInt(btn.dataset.page);
      if (p >= 1 && p <= totalPages && p !== currentPage) {
        currentPage = p;
        render();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });
}

function li(disabled, label, page, active = false) {
  return `<li class="page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}">
    <button class="page-link" data-page="${page}">${label}</button>
  </li>`;
}

// ── Načtení dat ───────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const grid    = document.getElementById('fileGrid');
  const spinner = document.createElement('div');
  spinner.className = 'col-12 text-center py-5';
  spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Načítání...</span></div>';
  grid.appendChild(spinner);

  fetch('/prohlizet/data')
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(files => {
      spinner.remove();
      allFiles = files;
      applyFiltersAndSort();
    })
    .catch(err => {
      console.error(err);
      spinner.remove();
      grid.innerHTML = `
        <div class="col-12">
          <div class="alert alert-danger text-center">
            Chyba při načítání dat ze serveru.
          </div>
        </div>`;
    });

  // živé filtrování
  document.getElementById('searchInput').addEventListener('input', applyFiltersAndSort);
  document.getElementById('sortSelect').addEventListener('change', applyFiltersAndSort);
  document.getElementById('perPageSelect').addEventListener('change', () => {
    itemsPerPage = parseInt(document.getElementById('perPageSelect').value);
    currentPage = 1;
    render();
  });
  document.getElementById('clearSearch').addEventListener('click', () => {
    document.getElementById('searchInput').value = '';
    applyFiltersAndSort();
    document.getElementById('searchInput').focus();
  });
});

// ── Otevření PDF modalu ───────────────────────────────────────────

function openPdfModal(pdfPath, filename) {
  const iframe = document.getElementById('pdfIframe');
  const label  = document.getElementById('pdfModalLabel');
  if (iframe) iframe.src = pdfPath;
  if (label)  label.textContent = filename;
  const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('pdfModal'));
  modal.show();
}
