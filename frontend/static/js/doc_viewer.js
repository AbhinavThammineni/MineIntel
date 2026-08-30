function openDocModal(docId, pageNum, snippet, bbox) {
  const modal = document.getElementById('doc-modal');
  const title = document.getElementById('modal-doc-title');
  const subtitle = document.getElementById('modal-doc-subtitle');
  const docPage = document.getElementById('simulated-doc-page');

  title.innerText = `Document Provenance: ${docId}`;
  subtitle.innerText = `Page ${pageNum || 1} • Token Bounding Box Coordinates: [${bbox ? `${bbox.x0 || 72}, ${bbox.y0 || 120}, ${bbox.x1 || 500}, ${bbox.y1 || 150}` : 'Default'}]`;

  docPage.innerHTML = `
    <div class="border-b border-slate-300 pb-3 mb-4 flex justify-between items-center text-slate-500 text-[11px]">
      <span>GOVERNMENT OF INDIA / COAL STATUTORY FILING</span>
      <span>${docId} | PAGE ${pageNum || 1}</span>
    </div>
    <div class="text-slate-400 text-[10px] mb-4 uppercase tracking-wider font-sans">
      Confidential Statutory Production & Geological Disclosure
    </div>
    <p class="text-slate-700 mb-4">
      The operational management of Coal India Limited and constituent subsidiaries hereby submits the audited operational throughput and field measurements for the declared period.
    </p>
    <div class="my-6 p-4 bg-amber-50 border-2 border-amber-400 rounded-lg shadow-md relative">
      <div class="absolute -top-3 left-4 bg-amber-500 text-white text-[9px] font-bold px-2 py-0.5 rounded shadow">
        <i class="fa-solid fa-crosshairs mr-1"></i> EXTRACTED BOUNDING BOX [Page ${pageNum || 1}]
      </div>
      <p class="text-slate-950 font-bold text-sm leading-relaxed mt-1">
        "${snippet || 'Mine A produced 12.5 MT of coal during 2023.'}"
      </p>
      <div class="mt-2 text-[10px] text-amber-900 flex items-center justify-between">
        <span>Verified Entity: Coal Production Fact</span>
        <span class="font-bold">Confidence: 99.8%</span>
      </div>
    </div>
    <p class="text-slate-600 mb-3">
      Field extraction data has been reconciled against railhead weighbridge dispatches, raw coal washery input tallies, and end-of-year aerial volumetric survey scans.
    </p>
    <div class="mt-8 pt-4 border-t border-slate-200 flex justify-between text-slate-400 text-[10px]">
      <span>Official Signature / Digital Certificate: VALID</span>
      <span>Audit Seal: STATUTORY VERIFIED</span>
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeDocModal() {
  document.getElementById('doc-modal').classList.add('hidden');
}
