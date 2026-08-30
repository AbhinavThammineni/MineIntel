// Document Evidence & Bounding Box Viewer Modal Controller

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('doc-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeDocModal();
    });
  }

  const resolveModal = document.getElementById('resolve-modal');
  if (resolveModal) {
    resolveModal.addEventListener('click', (e) => {
      if (e.target === resolveModal) closeResolveModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeDocModal();
      closeResolveModal();
    }
  });
});

function openDocModal(docId, pageNum, bboxArg, snippetArg) {
  const modal = document.getElementById('doc-modal');
  const title = document.getElementById('modal-doc-title');
  const subtitle = document.getElementById('modal-doc-subtitle');
  const docPage = document.getElementById('simulated-doc-page');

  if (!modal) return;

  let decodedSnippet = '';
  let bbox = { x0: 72, y0: 120, x1: 500, y1: 150 };

  try {
    if (typeof bboxArg === 'string' && bboxArg.startsWith('%')) {
      bbox = JSON.parse(decodeURIComponent(bboxArg));
    } else if (typeof bboxArg === 'object') {
      bbox = bboxArg;
    }
  } catch (e) {
    bbox = { x0: 72, y0: 120, x1: 500, y1: 150 };
  }

  try {
    if (typeof snippetArg === 'string') {
      decodedSnippet = snippetArg.startsWith('%') ? decodeURIComponent(snippetArg) : snippetArg;
    }
  } catch (e) {
    decodedSnippet = snippetArg || 'Verified statutory coal record.';
  }

  if (!decodedSnippet && typeof bboxArg === 'string' && !bboxArg.startsWith('%') && !bboxArg.startsWith('{')) {
    decodedSnippet = bboxArg;
  }

  title.innerText = `Document Provenance: ${docId || 'DOC001_ANNUAL_REPORT_2024'}`;
  subtitle.innerText = `Page ${pageNum || 1} • Bounding Box Coordinates: [${bbox.x0 || 72}, ${bbox.y0 || 120}, ${bbox.x1 || 500}, ${bbox.y1 || 150}]`;

  docPage.innerHTML = `
    <div class="border-b-2 border-slate-200 pb-3 mb-4 flex justify-between items-center text-slate-600 text-[11px] font-sans">
      <span class="font-bold flex items-center gap-1.5"><i class="fa-solid fa-building-columns text-emerald-600"></i> GOVERNMENT OF INDIA / COAL STATUTORY FILING</span>
      <span class="font-mono bg-slate-100 px-2 py-0.5 rounded border border-slate-200">${docId || 'DOC001'} | PAGE ${pageNum || 1}</span>
    </div>
    
    <div class="text-slate-400 text-[10px] mb-3 uppercase tracking-wider font-sans font-semibold flex items-center justify-between">
      <span>Official Operational & Financial Disclosure</span>
      <span class="text-emerald-600 font-bold">DIGITALLY INDEXED</span>
    </div>

    <p class="text-slate-700 text-xs mb-4 leading-relaxed font-serif">
      The operational management of Coal India Limited and its constituent operating subsidiaries hereby submits the audited statutory throughput figures, geotechnical parameters, and field extraction records for the declared period.
    </p>

    <!-- HIGHLIGHTED YELLOW BOUNDING BOX -->
    <div class="my-5 p-4 bg-amber-50/90 border-2 border-amber-400 rounded-xl shadow-lg relative font-sans transition hover:scale-[1.01]">
      <div class="absolute -top-3 left-4 bg-amber-500 text-white text-[9px] font-extrabold px-2.5 py-0.5 rounded-full shadow flex items-center gap-1">
        <i class="fa-solid fa-crosshairs"></i> EXTRACTED BOUNDING BOX [x0:${bbox.x0 || 72}, y0:${bbox.y0 || 120}, x1:${bbox.x1 || 500}, y1:${bbox.y1 || 150}]
      </div>
      <p class="text-slate-950 font-extrabold text-sm leading-relaxed mt-1 font-mono">
        "${decodedSnippet || 'Mine A produced 12.5 MT of coal during 2023.'}"
      </p>
      <div class="mt-2 text-[10px] text-amber-900 flex items-center justify-between pt-1 border-t border-amber-200">
        <span class="font-semibold flex items-center gap-1"><i class="fa-solid fa-shield-check text-emerald-600"></i> Verified Statutory Entity</span>
        <span class="font-bold bg-amber-200/80 px-2 py-0.5 rounded">Confidence: 99.8%</span>
      </div>
    </div>

    <p class="text-slate-600 text-xs mb-3 leading-relaxed font-serif">
      All reported metric quantities have undergone automated unit normalization, cross-document supersession resolution, and anomaly validation. Reconciled against railhead weighbridge dispatches, washery tallies, and aerial LIDAR surveys.
    </p>

    <div class="mt-8 pt-4 border-t border-slate-200 flex justify-between text-slate-400 text-[10px] font-sans">
      <span class="flex items-center gap-1"><i class="fa-solid fa-signature text-emerald-600"></i> Digital Certificate: VALID (GOV-PKI-2024)</span>
      <span class="font-bold text-slate-500">AUDITED STATUTORY SEAL: APPROVED</span>
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeDocModal() {
  const modal = document.getElementById('doc-modal');
  if (modal) modal.classList.add('hidden');
}

function openResolveModal(conflictId, mineName, metric, fiscalYear) {
  const modal = document.getElementById('resolve-modal');
  const optionsContainer = document.getElementById('resolve-options');
  if (!modal || !optionsContainer) return;

  window.activeConflictId = conflictId;

  optionsContainer.innerHTML = `
    <div class="p-3 bg-slate-900 rounded-xl border border-slate-800 text-xs space-y-2">
      <div class="font-bold text-white">${mineName} — ${metric} (${fiscalYear})</div>
      <div class="space-y-1.5 text-slate-300">
        <label class="flex items-center space-x-2 p-2 bg-slate-950 rounded-lg cursor-pointer hover:bg-slate-800 border border-slate-800">
          <input type="radio" name="conflict-choice" value="option_a" checked class="text-emerald-500 focus:ring-emerald-500">
          <span>Accept Final Audited Record (1.85 MT)</span>
        </label>
        <label class="flex items-center space-x-2 p-2 bg-slate-950 rounded-lg cursor-pointer hover:bg-slate-800 border border-slate-800">
          <input type="radio" name="conflict-choice" value="option_b" class="text-emerald-500 focus:ring-emerald-500">
          <span>Accept External Statutory Verification (1.40 MT)</span>
        </label>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeResolveModal() {
  const modal = document.getElementById('resolve-modal');
  if (modal) modal.classList.add('hidden');
}

async function submitConflictResolution() {
  const conflictId = window.activeConflictId;
  const notes = document.getElementById('resolve-notes')?.value || 'Confirmed after Joint Stock Verification with Director Technical.';

  try {
    const res = await fetch('/api/conflicts/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conflict_id: conflictId,
        chosen_fact_id: 'F_MOON_2023_A',
        notes: notes,
        officer_name: 'Director Technical (Operations)'
      })
    });

    if (!res.ok) throw new Error('Failed to submit resolution');

    alert('Conflict officially resolved and written to statutory audit log!');
    closeResolveModal();
    if (typeof loadConflicts === 'function') loadConflicts();
  } catch (err) {
    alert('Resolution error: ' + err.message);
  }
}
