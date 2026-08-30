async function generateParliamentaryDraft(e) {
  e.preventDefault();
  const qNo = document.getElementById('parl-q-no').value;
  const session = document.getElementById('parl-session').value;
  const house = document.getElementById('parl-house').value;
  const qText = document.getElementById('parl-q-text').value;
  const container = document.getElementById('parliament-draft-container');

  container.innerHTML = `
    <div class="bg-coal-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 space-y-3">
      <i class="fa-solid fa-landmark-flag fa-bounce text-emerald-400 text-3xl"></i>
      <p class="text-xs">Executing deterministic math on statutory database, compiling Annexures, and drafting official ministry reply...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/parliament/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_no: qNo, session: session, house: house, question_text: qText })
    });
    const draft = await res.json();

    renderParliamentaryDraft(draft);

  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400">Failed to draft response: ${err.message}</div>`;
  }
}

function renderParliamentaryDraft(draft) {
  const container = document.getElementById('parliament-draft-container');
  
  let annexureRows = '';
  if (draft.annexure_table && draft.annexure_table.length > 0) {
    annexureRows = draft.annexure_table.map(s => `
      <tr class="hover:bg-slate-800/40">
        <td class="p-2.5 font-bold text-white">${s.subsidiary}</td>
        <td class="p-2.5 text-center">${s.start_year_val}</td>
        <td class="p-2.5 text-center font-bold text-emerald-400">${s.end_year_val}</td>
        <td class="p-2.5 text-center ${s.total_growth_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'} font-semibold">${s.total_growth_pct > 0 ? '+' : ''}${s.total_growth_pct}%</td>
        <td class="p-2.5 text-center">${s.cagr_pct ? `${s.cagr_pct}%` : 'N/A'}</td>
      </tr>
    `).join('');
  }

  const isApproved = draft.approval_status === 'Approved';

  container.innerHTML = `
    <div class="bg-coal-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-5 gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 text-xs font-bold ${isApproved ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'} rounded-full">
              Status: ${draft.approval_status}
            </span>
            <span class="text-xs text-slate-400">${draft.session} • ${draft.house}</span>
          </div>
          <h3 class="text-lg font-bold text-white mt-1.5">${draft.question_no}: ${draft.question_text}</h3>
        </div>
        
        <div class="flex items-center space-x-2">
          ${!isApproved ? `
            <button onclick="approveDraft('${draft.id}')" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-md transition flex items-center gap-1.5">
              <i class="fa-solid fa-signature"></i>
              <span>Approve & Sign-Off</span>
            </button>
          ` : `
            <span class="px-3 py-1.5 bg-emerald-950 text-emerald-300 border border-emerald-500/40 rounded-lg text-xs font-semibold flex items-center gap-1.5">
              <i class="fa-solid fa-badge-check text-emerald-400"></i>
              <span>Signed by: ${draft.approved_by || 'Officer In-Charge'}</span>
            </span>
          `}
        </div>
      </div>

      <div class="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
${draft.drafted_response}
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">ANNEXURE-I: SUBSIDIARY PRODUCTION & GROWTH METRICS (IN MILLION TONNES)</h4>
        <div class="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                <th class="p-2.5">Subsidiary</th>
                <th class="p-2.5 text-center">FY 2021-22</th>
                <th class="p-2.5 text-center">FY 2024-25</th>
                <th class="p-2.5 text-center">Growth (%)</th>
                <th class="p-2.5 text-center">CAGR (%)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              ${annexureRows}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

async function approveDraft(draftId) {
  try {
    const res = await fetch('/api/parliament/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draft_id: draftId,
        approval_status: 'Approved',
        approved_by: 'Under Secretary (Coal Operations), Ministry of Coal'
      })
    });
    const data = await res.json();
    alert('Parliamentary Statement officially approved and signed!');
    const draftsRes = await fetch('/api/parliament/list');
    const drafts = await draftsRes.json();
    if (drafts.length > 0) renderParliamentaryDraft(drafts[0]);
  } catch (err) {
    alert('Failed to approve draft: ' + err.message);
  }
}
