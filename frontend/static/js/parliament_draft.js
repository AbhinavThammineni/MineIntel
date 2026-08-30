async function generateParliamentaryDraft(e) {
  if (e && e.preventDefault) e.preventDefault();
  
  const qNo = document.getElementById('parl-q-no')?.value || 'Starred Question No. 184';
  const session = document.getElementById('parl-session')?.value || 'Monsoon Session 2024';
  const house = document.getElementById('parl-house')?.value || 'Lok Sabha';
  const qText = document.getElementById('parl-q-text')?.value || 'Provide subsidiary-wise coal production of Coal India Limited from 2021 to 2025 and explain the major operational variations.';
  const container = document.getElementById('parliament-draft-container');

  if (!container) return;

  container.innerHTML = `
    <div class="glass-card rounded-2xl p-12 text-center text-slate-400 space-y-3 border border-slate-800">
      <i class="fa-solid fa-landmark-dome fa-bounce text-emerald-400 text-3xl"></i>
      <p class="text-xs">Executing deterministic math on statutory database, compiling Annexure-I, and drafting official ministry reply...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/parliament/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_no: qNo, session: session, house: house, question_text: qText })
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Server returned error (${res.status}): ${errText}`);
    }

    const draft = await res.json();
    renderParliamentaryDraft(draft);

  } catch (err) {
    container.innerHTML = `
      <div class="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-xs text-red-400 space-y-2">
        <div class="font-bold flex items-center gap-2"><i class="fa-solid fa-circle-exclamation"></i> Error Drafting Parliamentary Statement</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderParliamentaryDraft(draft) {
  const container = document.getElementById('parliament-draft-container');
  if (!container) return;
  
  let annexureRows = '';
  if (draft.annexure_table && draft.annexure_table.length > 0) {
    annexureRows = draft.annexure_table.map(s => `
      <tr class="hover:bg-slate-800/40">
        <td class="p-3 font-bold text-white">${s.subsidiary}</td>
        <td class="p-3 text-center text-slate-300">${s.start_year_val} MT</td>
        <td class="p-3 text-center font-bold text-emerald-400">${s.end_year_val} MT</td>
        <td class="p-3 text-center ${s.total_growth_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'} font-semibold">${s.total_growth_pct > 0 ? '+' : ''}${s.total_growth_pct}%</td>
        <td class="p-3 text-center font-semibold text-slate-300">${s.cagr_pct ? `${s.cagr_pct}%` : 'N/A'}</td>
      </tr>
    `).join('');
  }

  const isApproved = draft.approval_status === 'Approved';

  container.innerHTML = `
    <div class="glass-card rounded-2xl p-8 shadow-2xl space-y-6 border border-slate-800">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-5 gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-0.5 text-[11px] font-bold ${isApproved ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'} rounded-full">
              Status: ${draft.approval_status}
            </span>
            <span class="text-xs text-slate-400 font-medium">${draft.session} • ${draft.house}</span>
          </div>
          <h3 class="text-lg font-bold text-white mt-1.5">${draft.question_no}: ${draft.question_text}</h3>
        </div>
        
        <div class="flex items-center space-x-2">
          ${!isApproved ? `
            <button onclick="approveDraft('${draft.id}')" class="btn-shimmer px-4 py-2 text-white text-xs font-bold rounded-xl shadow-lg transition flex items-center gap-1.5 hover:scale-[1.02]">
              <i class="fa-solid fa-signature"></i>
              <span>Approve & Sign-Off</span>
            </button>
          ` : `
            <span class="px-3 py-1.5 bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-semibold flex items-center gap-1.5">
              <i class="fa-solid fa-circle-check text-emerald-400"></i>
              <span>Officially Signed by: ${draft.approved_by || 'Under Secretary (Coal Operations)'}</span>
            </span>
          `}
        </div>
      </div>

      <!-- Formal Ministry Laid on Table Statement -->
      <div class="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap shadow-inner">
${draft.drafted_response}
      </div>

      <!-- Annexure-I -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-table text-emerald-400"></i>
            ANNEXURE-I: SUBSIDIARY-WISE PRODUCTION & CAGR METRICS
          </h4>
          <span class="text-[10px] text-slate-500 font-mono">CONFIDENTIAL OFFICIAL PARLIAMENTARY RECORD</span>
        </div>
        <div class="overflow-x-auto border border-slate-800 rounded-xl bg-slate-950">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                <th class="p-3">Subsidiary</th>
                <th class="p-3 text-center">FY 2021-22</th>
                <th class="p-3 text-center">FY 2024-25</th>
                <th class="p-3 text-center">Growth (%)</th>
                <th class="p-3 text-center">CAGR (%)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
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
    if (!res.ok) throw new Error('Failed to approve draft on server');
    
    alert('✅ Parliamentary Statement officially approved and signed into statutory record!');
    const draftsRes = await fetch('/api/parliament/list');
    if (draftsRes.ok) {
      const drafts = await draftsRes.json();
      if (drafts.length > 0) renderParliamentaryDraft(drafts[0]);
    }
  } catch (err) {
    alert('Failed to approve draft: ' + err.message);
  }
}
