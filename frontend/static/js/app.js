// MineIntel Core Frontend Controller

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  loadConflicts();
  loadIngestedDocuments();
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => {
    el.classList.remove('active', 'border-emerald-500', 'text-emerald-400');
    el.classList.add('border-transparent', 'text-slate-400');
  });

  const activeContent = document.getElementById(`tab-${tabId}`);
  if (activeContent) activeContent.classList.remove('hidden');

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'border-emerald-500', 'text-emerald-400');
    activeBtn.classList.remove('border-transparent', 'text-slate-400');
  }

  // Handle GIS Map display and size invalidation
  if (tabId === 'gis' && typeof onGisTabActivated === 'function') {
    onGisTabActivated();
  }
}

function setQuery(queryText) {
  const input = document.getElementById('qa-input');
  if (input) {
    input.value = queryText;
    switchTab('qa');
    const form = document.getElementById('qa-form');
    if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
  }
}

async function handleQuerySubmit(e) {
  if (e && e.preventDefault) e.preventDefault();
  const input = document.getElementById('qa-input');
  const query = input?.value?.trim();
  if (!query) return;

  const resultsContainer = document.getElementById('qa-results');
  if (!resultsContainer) return;

  resultsContainer.innerHTML = `
    <div class="glass-card rounded-2xl p-8 sm:p-12 text-center text-slate-400 space-y-3 border border-slate-800">
      <i class="fa-solid fa-circle-notch fa-spin text-emerald-400 text-3xl"></i>
      <p class="text-xs">Querying PostgreSQL facts, searching pgvector semantic passages, and retrieving bounding box provenance...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/qa/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Server returned error (${res.status}): ${errText}`);
    }

    const data = await res.json();
    renderQaResponse(data, query);
  } catch (err) {
    resultsContainer.innerHTML = `
      <div class="p-4 sm:p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-xs text-red-400 space-y-2">
        <div class="font-bold flex items-center gap-2"><i class="fa-solid fa-circle-exclamation"></i> Query Execution Error</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderQaResponse(data, originalQuery) {
  const container = document.getElementById('qa-results');
  if (!container) return;

  let citationsHtml = '';
  if (data.citations && data.citations.length > 0) {
    citationsHtml = data.citations.map(c => `
      <div class="p-3 sm:p-4 bg-slate-950/90 rounded-xl border border-slate-800 space-y-2">
        <div class="flex flex-wrap items-center justify-between gap-1">
          <span class="text-[11px] font-bold text-emerald-400 flex items-center gap-1.5 truncate">
            <i class="fa-solid fa-file-pdf"></i> ${c.doc_id}
          </span>
          <span class="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded font-medium">Page ${c.page_number}</span>
        </div>
        <p class="text-xs text-slate-300 italic font-mono bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80">"${c.snippet || 'Verified data record'}"</p>
        <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1">
          <span>Confidence: <strong class="text-slate-300">${((c.confidence || 0.99) * 100).toFixed(0)}%</strong></span>
          <button onclick="openDocModal('${c.doc_id}', ${c.page_number}, '${encodeURIComponent(JSON.stringify(c.bbox || {}))}', '${encodeURIComponent(c.snippet || '')}')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 hover:text-white rounded-lg text-xs font-semibold transition border border-slate-700 shadow-sm flex items-center gap-1">
            <i class="fa-solid fa-magnifying-glass"></i>
            <span>Inspect Box</span>
          </button>
        </div>
      </div>
    `).join('');
  }

  let notesHtml = '';
  if (data.notes && data.notes.length > 0) {
    notesHtml = data.notes.map(n => `
      <div class="p-3 bg-blue-950/40 border border-blue-600/30 rounded-xl text-xs text-blue-300 flex items-start gap-2">
        <i class="fa-solid fa-circle-info text-blue-400 mt-0.5 flex-shrink-0"></i>
        <span>${n}</span>
      </div>
    `).join('');
  }

  container.innerHTML = `
    <div class="glass-card rounded-2xl p-4 sm:p-7 shadow-2xl space-y-4 border border-slate-800">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-1.5">
        <span class="text-xs text-slate-400 font-medium truncate">
          <i class="fa-solid fa-user-circle text-slate-500 mr-1"></i> Query: "${originalQuery}"
        </span>
        <span class="self-start sm:self-auto px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
          ${data.query_type}
        </span>
      </div>

      <!-- Markdown Answer Content -->
      <div class="text-xs sm:text-sm text-slate-200 leading-relaxed space-y-2">
        ${renderMarkdownText(data.answer)}
      </div>

      ${notesHtml}

      <!-- Verified Provenance Citations Section -->
      ${citationsHtml ? `
        <div class="space-y-2 pt-2 border-t border-slate-800">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <i class="fa-solid fa-award text-emerald-400"></i> Verified Statutory Citations & Bounding Boxes
          </h4>
          <div class="grid grid-cols-1 gap-2">
            ${citationsHtml}
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

function renderMarkdownText(txt) {
  if (!txt) return '';
  let html = txt
    .replace(/^### (.*$)/gim, '<h3 class="text-xs sm:text-sm font-bold text-white mt-2 mb-1">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-sm sm:text-base font-bold text-white mt-3 mb-1">$1</h2>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em class="text-slate-300">$1</em>');

  // Convert markdown tables to styled responsive HTML tables
  if (html.includes('|')) {
    const lines = html.split('\n');
    let inTable = false;
    let tableHtml = '<div class="table-responsive-wrapper my-2 border border-slate-800 rounded-xl bg-slate-950"><table class="w-full text-left text-xs border-collapse min-w-[500px]">';
    let resultLines = [];

    for (let line of lines) {
      if (line.trim().startsWith('|')) {
        if (!inTable) {
          inTable = true;
          tableHtml = '<div class="table-responsive-wrapper my-2 border border-slate-800 rounded-xl bg-slate-950"><table class="w-full text-left text-xs border-collapse min-w-[500px]">';
        }
        if (line.includes(':---') || line.includes('---:')) {
          continue;
        }
        const cells = line.split('|').filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
        const isHeader = !tableHtml.includes('<tbody>');
        if (isHeader) {
          tableHtml += '<thead class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]"><tr>';
          cells.forEach(c => { tableHtml += `<th class="p-3">${c.trim()}</th>`; });
          tableHtml += '</tr></thead><tbody>';
        } else {
          tableHtml += '<tr class="hover:bg-slate-800/40 border-b border-slate-800/50">';
          cells.forEach(c => { tableHtml += `<td class="p-3 text-slate-200">${c.trim()}</td>`; });
          tableHtml += '</tr>';
        }
      } else {
        if (inTable) {
          inTable = false;
          tableHtml += '</tbody></table></div>';
          resultLines.push(tableHtml);
        }
        if (line.trim()) resultLines.push(`<p class="my-1">${line}</p>`);
      }
    }
    if (inTable) {
      tableHtml += '</tbody></table></div>';
      resultLines.push(tableHtml);
    }
    return resultLines.join('');
  }

  return `<p class="whitespace-pre-wrap">${html}</p>`;
}

async function loadConflicts() {
  const container = document.getElementById('conflicts-list-container');
  if (!container) return;

  try {
    const res = await fetch('/api/conflicts/list');
    if (!res.ok) return;
    const conflicts = await res.json();

    const badge = document.getElementById('badge-conflict-count');
    if (badge) {
      const activeCount = conflicts.filter(c => c.status === 'under_review').length;
      badge.textContent = activeCount;
      badge.className = activeCount > 0 
        ? 'ml-1 px-1.5 py-0.5 text-[9px] bg-red-500/20 text-red-400 border border-red-500/40 rounded-full font-extrabold shadow-sm'
        : 'ml-1 px-1.5 py-0.5 text-[9px] bg-slate-800 text-slate-400 rounded-full font-medium';
    }

    if (conflicts.length === 0) {
      container.innerHTML = `<div class="p-6 bg-slate-900 border border-slate-800 rounded-2xl text-center text-xs text-slate-400">All multi-document statutory records are reconciled and consistent.</div>`;
      return;
    }

    // 1. MOBILE RESPONSIVE CARDS (Visible on phone screens < 768px)
    const mobileCardsHtml = `
      <div class="md:hidden space-y-3">
        ${conflicts.map(c => `
          <div class="glass-card rounded-2xl p-4 border border-slate-800 space-y-3 shadow-lg">
            <div class="flex items-start justify-between gap-2 border-b border-slate-800 pb-2.5">
              <div>
                <h4 class="font-bold text-white text-xs sm:text-sm">${c.mine_name}</h4>
                <p class="text-[11px] text-slate-400">${c.metric} • ${c.fiscal_year}</p>
              </div>
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full flex-shrink-0 ${c.status === 'superseded' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'}">
                ${c.status.toUpperCase()}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 uppercase font-semibold">Variance Delta</span>
                <p class="font-bold font-mono ${c.discrepancy_delta > 1.0 ? 'text-rose-400' : 'text-amber-400'}">${c.discrepancy_delta} MT</p>
              </div>
              <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span class="text-[10px] text-slate-500 uppercase font-semibold">Classification</span>
                <p class="font-semibold text-slate-300 text-[11px]">${c.conflict_type === 'superseded_discrepancy' ? 'Supersession' : 'Genuine Conflict'}</p>
              </div>
            </div>

            <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-[11px] space-y-1">
              <span class="text-slate-400 font-semibold block text-[10px] uppercase tracking-wider">Resolution Trail & Notes:</span>
              <p class="text-slate-300 leading-relaxed">${c.resolution_notes}</p>
            </div>

            <!-- Mobile Action Button -->
            <div class="pt-1">
              ${c.status === 'under_review' ? `
                <button onclick="openResolveModal('${c.id}', '${c.mine_name}', '${c.metric}', '${c.fiscal_year}')" class="w-full py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition shadow-sm flex items-center justify-center gap-1.5">
                  <i class="fa-solid fa-gavel"></i>
                  <span>Resolve & Sign-Off Discrepancy</span>
                </button>
              ` : `
                <div class="w-full py-2 bg-slate-900 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5">
                  <i class="fa-solid fa-circle-check"></i>
                  <span>Statutorily Reconciled & Audited</span>
                </div>
              `}
            </div>
          </div>
        `).join('')}
      </div>
    `;

    // 2. DESKTOP RESPONSIVE TABLE (Visible on tablets and laptops >= 768px)
    const desktopTableHtml = `
      <div class="hidden md:block glass-card rounded-2xl overflow-hidden border border-slate-800 shadow-2xl table-responsive-wrapper">
        <table class="w-full text-left text-xs border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
              <th class="p-3.5">Entity / Metric</th>
              <th class="p-3.5 text-center">Variance (Delta)</th>
              <th class="p-3.5 text-center">Classification</th>
              <th class="p-3.5 text-center">Status</th>
              <th class="p-3.5">Resolution Trail</th>
              <th class="p-3.5 text-center">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            ${conflicts.map(c => `
              <tr class="hover:bg-slate-800/40">
                <td class="p-3.5 font-bold text-white">${c.mine_name}<br><span class="text-[11px] font-normal text-slate-400">${c.metric} (${c.fiscal_year})</span></td>
                <td class="p-3.5 text-center font-mono font-bold ${c.discrepancy_delta > 1.0 ? 'text-rose-400' : 'text-amber-400'}">${c.discrepancy_delta} MT</td>
                <td class="p-3.5 text-center text-slate-300 text-[11px]">${c.conflict_type === 'superseded_discrepancy' ? 'Supersession' : 'Genuine Conflict'}</td>
                <td class="p-3.5 text-center">
                  <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full ${c.status === 'superseded' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'}">
                    ${c.status.toUpperCase()}
                  </span>
                </td>
                <td class="p-3.5 text-slate-300 text-[11px] max-w-xs leading-relaxed">${c.resolution_notes}</td>
                <td class="p-3.5 text-center">
                  ${c.status === 'under_review' ? `
                    <button onclick="openResolveModal('${c.id}', '${c.mine_name}', '${c.metric}', '${c.fiscal_year}')" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-bold transition shadow-sm">
                      Resolve
                    </button>
                  ` : `
                    <span class="text-slate-500 text-xs"><i class="fa-solid fa-circle-check text-emerald-400 mr-1"></i> Audited</span>
                  `}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = mobileCardsHtml + desktopTableHtml;

  } catch (err) {
    console.error('Error loading conflicts:', err);
  }
}

async function loadIngestedDocuments() {
  const container = document.getElementById('ingested-docs-container');
  if (!container) return;

  try {
    const res = await fetch('/api/ingest/documents');
    if (!res.ok) return;
    const docs = await res.json();

    if (docs.length === 0) {
      container.innerHTML = `<div class="p-6 bg-slate-900 border border-slate-800 rounded-2xl text-center text-xs text-slate-400">No documents ingested yet.</div>`;
      return;
    }

    // Mobile Cards
    const mobileDocsHtml = `
      <div class="md:hidden space-y-2.5">
        ${docs.map(d => `
          <div class="glass-card rounded-xl p-3.5 border border-slate-800 space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div>
                <h4 class="font-bold text-white text-xs">${d.title}</h4>
                <p class="text-[10px] text-slate-500 font-mono">${d.id}</p>
              </div>
              <span class="px-2 py-0.5 text-[9px] font-bold uppercase bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-full flex-shrink-0">
                ${d.file_type}
              </span>
            </div>
            <div class="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800 text-slate-400">
              <span>Pages: <strong class="text-white">${d.total_pages}</strong></span>
              <span class="text-emerald-400 font-semibold"><i class="fa-solid fa-circle-check mr-1"></i> Indexed</span>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    // Desktop Table
    const desktopDocsHtml = `
      <div class="hidden md:block glass-card rounded-2xl overflow-hidden border border-slate-800 shadow-2xl table-responsive-wrapper">
        <table class="w-full text-left text-xs border-collapse min-w-[650px]">
          <thead>
            <tr class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
              <th class="p-3.5">Document Title / ID</th>
              <th class="p-3.5 text-center">Type</th>
              <th class="p-3.5 text-center">Authority Classification</th>
              <th class="p-3.5 text-center">Pages</th>
              <th class="p-3.5 text-center">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            ${docs.map(d => `
              <tr class="hover:bg-slate-800/40">
                <td class="p-3.5 font-bold text-white">${d.title}<br><span class="text-[10px] text-slate-500 font-mono">${d.id}</span></td>
                <td class="p-3.5 text-center text-slate-400 uppercase font-mono">${d.file_type}</td>
                <td class="p-3.5 text-center"><span class="px-2.5 py-0.5 text-[10px] font-bold bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-full">${d.doc_type}</span></td>
                <td class="p-3.5 text-center text-slate-300 font-bold">${d.total_pages}</td>
                <td class="p-3.5 text-center"><span class="text-emerald-400 text-xs font-semibold"><i class="fa-solid fa-circle-check mr-1"></i> Indexed</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = mobileDocsHtml + desktopDocsHtml;

  } catch (err) {
    console.error('Error loading documents:', err);
  }
}

async function triggerEvidenceEngine() {
  try {
    const res = await fetch('/api/conflicts/trigger', { method: 'POST' });
    if (res.ok) {
      alert('Evidence Consistency Engine executed: all cross-document supersessions and genuine conflicts re-evaluated.');
      loadConflicts();
    }
  } catch (err) {
    alert('Error running evidence engine: ' + err.message);
  }
}
