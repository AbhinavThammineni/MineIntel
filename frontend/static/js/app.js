let activeConflictId = null;

document.addEventListener('DOMContentLoaded', () => {
  loadConflicts();
  loadDocuments();
});

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active', 'border-emerald-500', 'text-emerald-400');
    btn.classList.add('border-transparent', 'text-slate-400');
  });
  document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.add('active', 'border-emerald-500', 'text-emerald-400');
    activeBtn.classList.remove('border-transparent', 'text-slate-400');
  }

  const activeContent = document.getElementById(`tab-${tabId}`);
  if (activeContent) activeContent.classList.remove('hidden');

  if (tabId === 'gis') {
    initGISMap();
  } else if (tabId === 'reports') {
    generateReport();
  } else if (tabId === 'conflicts') {
    loadConflicts();
  } else if (tabId === 'ingest') {
    loadDocuments();
  }
}

function setQuery(text) {
  document.getElementById('qa-input').value = text;
  document.getElementById('qa-form').dispatchEvent(new Event('submit'));
}

async function handleQuerySubmit(e) {
  e.preventDefault();
  const input = document.getElementById('qa-input');
  const query = input.value.trim();
  if (!query) return;

  const feed = document.getElementById('qa-results');
  const submitBtn = document.getElementById('qa-submit-btn');

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs"></i>';

  try {
    const res = await fetch('/api/qa/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });
    const data = await res.json();

    let citationsHtml = '';
    if (data.citations && data.citations.length > 0) {
      citationsHtml = `
        <div class="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Verifiable Evidence Citations</span>
          <div class="flex flex-wrap gap-2">
            ${data.citations.map(c => `
              <button onclick="openDocModal('${c.doc_id}', ${c.page_number}, '${(c.snippet || '').replace(/'/g, "\\'")}', ${JSON.stringify(c.bbox || {})})" class="px-3 py-1.5 bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-500/40 text-emerald-300 text-xs rounded-lg transition font-medium flex items-center gap-2 shadow-sm">
                <i class="fa-solid fa-file-certificate text-emerald-400"></i>
                <span>${c.doc_id} • Page ${c.page_number}</span>
                <span class="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 text-[10px] rounded">${Math.round(c.confidence * 100)}% verified</span>
              </button>
            `).join('')}
          </div>
        </div>
      `;
    }

    let notesHtml = '';
    if (data.notes && data.notes.length > 0) {
      notesHtml = data.notes.map(n => `<div class="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-lg mt-2">${n}</div>`).join('');
    }

    const card = document.createElement('div');
    card.className = 'bg-coal-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3 animate-in fade-in duration-300';
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="px-2.5 py-1 text-xs font-semibold bg-slate-800 text-slate-300 rounded-lg">Query: "${data.query}"</span>
        <span class="text-[11px] text-emerald-400 font-bold uppercase tracking-wider"><i class="fa-solid fa-check-double mr-1"></i> Deterministic Verified</span>
      </div>
      <div class="text-sm text-slate-100 leading-relaxed font-sans prose prose-invert">
        ${data.answer.replace(/\n/g, '<br>')}
      </div>
      ${notesHtml}
      ${citationsHtml}
    `;

    feed.prepend(card);

  } catch (err) {
    alert('Query failed: ' + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span>Query</span> <i class="fa-solid fa-paper-plane text-xs"></i>';
  }
}

async function loadConflicts() {
  const container = document.getElementById('conflicts-list-container');
  try {
    const res = await fetch('/api/conflicts/list');
    const conflicts = await res.json();

    const countBadge = document.getElementById('badge-conflict-count');
    const underReviewCount = conflicts.filter(c => c.status === 'under_review').length;
    if (countBadge) countBadge.innerText = underReviewCount;

    if (conflicts.length === 0) {
      container.innerHTML = `<div class="p-8 bg-coal-900 border border-slate-800 rounded-2xl text-center text-xs text-slate-400">All multi-document records are consistent. Zero discrepancies detected.</div>`;
      return;
    }

    container.innerHTML = conflicts.map(c => {
      const isGenuine = c.conflict_type === 'genuine_conflict';
      const isResolved = c.status === 'resolved';

      return `
        <div class="bg-coal-900 border ${isGenuine && !isResolved ? 'border-red-500/40' : 'border-slate-800'} rounded-2xl p-6 shadow-xl space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2.5">
              <span class="px-2.5 py-1 text-xs font-bold rounded-lg ${isGenuine ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}">
                ${c.conflict_type === 'superseded_discrepancy' ? 'Superseded Discrepancy' : 'Genuine Conflict (Human Review)'}
              </span>
              <h3 class="text-sm font-bold text-white">${c.mine_name} • ${c.metric} (${c.fiscal_year})</h3>
            </div>
            <span class="text-xs text-slate-400 font-mono">Discrepancy Δ: <strong>${c.discrepancy_delta} MT</strong></span>
          </div>

          <p class="text-xs text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-800">${c.resolution_notes}</p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            ${c.records_involved.map(r => `
              <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1.5">
                <div class="flex justify-between text-[11px]">
                  <span class="font-bold text-white">${r.doc_id} (Page ${r.page_number})</span>
                  <span class="text-emerald-400 font-bold">${r.normalized_value} ${r.normalized_unit}</span>
                </div>
                <p class="text-[11px] text-slate-400">${r.doc_type}</p>
                <button onclick="openDocModal('${r.doc_id}', ${r.page_number}, '${(r.raw_text || '').replace(/'/g, "\\'")}')" class="text-[10px] text-emerald-400 hover:underline flex items-center gap-1 font-semibold">
                  <i class="fa-solid fa-file-lines"></i> View Original Text
                </button>
              </div>
            `).join('')}
          </div>

          ${isGenuine && !isResolved ? `
            <div class="flex justify-end pt-2">
              <button onclick="openResolveModal('${c.id}', ${JSON.stringify(c.records_involved).replace(/"/g, '&quot;')})" class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-lg shadow transition flex items-center gap-2">
                <i class="fa-solid fa-gavel"></i>
                <span>Resolve Discrepancy</span>
              </button>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');

  } catch (err) {
    console.error('Failed to load conflicts:', err);
  }
}

function openResolveModal(conflictId, records) {
  activeConflictId = conflictId;
  const modal = document.getElementById('resolve-modal');
  const optContainer = document.getElementById('resolve-options');

  optContainer.innerHTML = records.map((r, idx) => `
    <label class="flex items-center space-x-3 p-3 bg-slate-950 border border-slate-800 rounded-xl cursor-pointer hover:border-emerald-500">
      <input type="radio" name="chosen_record" value="${r.id}" ${idx === 0 ? 'checked' : ''} class="text-emerald-500 focus:ring-emerald-500">
      <div class="text-xs">
        <span class="font-bold text-white">${r.normalized_value} ${r.normalized_unit}</span>
        <span class="text-slate-400 ml-2">from ${r.doc_id} (Page ${r.page_number})</span>
      </div>
    </label>
  `).join('');

  modal.classList.remove('hidden');
}

function closeResolveModal() {
  document.getElementById('resolve-modal').classList.add('hidden');
  activeConflictId = null;
}

async function submitConflictResolution() {
  if (!activeConflictId) return;
  const chosenInput = document.querySelector('input[name="chosen_record"]:checked');
  const notes = document.getElementById('resolve-notes').value.trim() || 'Resolved following officer audit review.';

  try {
    const res = await fetch('/api/conflicts/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conflict_id: activeConflictId,
        chosen_record_id: chosenInput.value,
        resolution_notes: notes,
        resolved_by: 'Director (Coal Statistics)'
      })
    });
    closeResolveModal();
    alert('Discrepancy resolved and Fact Store audit history updated!');
    loadConflicts();
  } catch (err) {
    alert('Failed to resolve conflict: ' + err.message);
  }
}

async function triggerEvidenceEngine() {
  try {
    const res = await fetch('/api/conflicts/trigger_evidence_engine', { method: 'POST' });
    const data = await res.json();
    alert('Evidence & Consistency Engine completed successfully!');
    loadConflicts();
  } catch (err) {
    alert('Failed: ' + err.message);
  }
}

async function handleDocUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('ingest-file');
  const docType = document.getElementById('ingest-doc-type').value;
  if (!fileInput.files[0]) return;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('doc_type', docType);

  try {
    const res = await fetch('/api/ingest/upload', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    alert(`Document ${result.filename} ingested! Extracted ${result.facts_extracted_count} structured facts with bounding boxes.`);
    loadDocuments();
    fileInput.value = '';
  } catch (err) {
    alert('Upload failed: ' + err.message);
  }
}

async function loadDocuments() {
  const container = document.getElementById('ingested-docs-container');
  try {
    const res = await fetch('/api/ingest/documents');
    const docs = await res.json();

    container.innerHTML = `
      <div class="bg-coal-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h3 class="text-sm font-bold text-white">Ingested Document Repository (${docs.length} Authority Sources)</h3>
        <div class="divide-y divide-slate-800 text-xs">
          ${docs.map(d => `
            <div class="py-3 flex items-center justify-between">
              <div>
                <p class="font-bold text-slate-200">${d.title || d.filename}</p>
                <p class="text-slate-400 text-[11px]">${d.doc_type} • ID: ${d.id} • ${d.page_count} Pages</p>
              </div>
              <button onclick="openDocModal('${d.id}', 1, 'Inspecting Document ${d.id}')" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition border border-slate-700 text-xs">
                Inspect Pages
              </button>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    console.error('Failed to load docs:', err);
  }
}
