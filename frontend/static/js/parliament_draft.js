// Parliamentary Drafts & RBAC Officer Authentication Controller

let currentOfficerRole = 'analyst'; // 'analyst' (read-only) or 'approver' (authorized)
let authenticatedOfficerName = 'Under Secretary (Coal Operations), Ministry of Coal';

document.addEventListener('DOMContentLoaded', () => {
  loadSavedDraftsArchive();
});

function toggleOfficerAuth() {
  if (currentOfficerRole === 'analyst') {
    const pin = prompt('Government e-Sign Gateway\nEnter Official Security PIN to authenticate as Approving Officer (Demo PIN: 1234):');
    if (pin === '1234') {
      currentOfficerRole = 'approver';
      updateAuthUI();
      alert('Authenticated as: Under Secretary (Coal Operations)\nAuthorization: Statutory Digital Approval & Sign-Off UNLOCKED.');
    } else if (pin !== null) {
      alert('Invalid Security PIN. Access denied. (Use Demo PIN: 1234)');
    }
  } else {
    currentOfficerRole = 'analyst';
    updateAuthUI();
    alert('Logged out from Approver role. Returned to Analyst (View-Only) mode.');
  }
}

function updateAuthUI() {
  const badge = document.getElementById('officer-role-badge');
  if (badge) {
    if (currentOfficerRole === 'approver') {
      badge.innerHTML = `
        <span class="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer hover:bg-emerald-500/30 transition shadow-sm" onclick="toggleOfficerAuth()">
          <i class="fa-solid fa-user-shield text-emerald-400"></i>
          <span>Role: Approving Officer (Authenticated)</span>
          <i class="fa-solid fa-arrow-right-from-bracket ml-1 text-slate-400 text-[10px]" title="Switch to Analyst"></i>
        </span>
      `;
    } else {
      badge.innerHTML = `
        <span class="px-3 py-1.5 bg-slate-900 text-slate-300 border border-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer hover:border-emerald-500 transition shadow-sm" onclick="toggleOfficerAuth()">
          <i class="fa-solid fa-user text-slate-400"></i>
          <span>Role: Analyst (View-Only)</span>
          <span class="text-[10px] text-emerald-400 underline ml-1">[Unlock Approver PIN]</span>
        </span>
      `;
    }
  }

  if (window.activeDraftObj) {
    renderParliamentaryDraft(window.activeDraftObj);
  }
}

async function generateParliamentaryDraft(e) {
  if (e && e.preventDefault) e.preventDefault();
  
  const qNo = document.getElementById('parl-q-no')?.value || 'Starred Question No. 184';
  const session = document.getElementById('parl-session')?.value || 'Monsoon Session 2024';
  const house = document.getElementById('parl-house')?.value || 'Lok Sabha';
  const qText = document.getElementById('parl-q-text')?.value || 'Provide subsidiary-wise coal production of Coal India Limited from 2021 to 2025 and explain the major operational variations.';
  const container = document.getElementById('parliament-draft-container');

  if (!container) return;

  container.innerHTML = `
    <div class="glass-card rounded-2xl p-8 sm:p-12 text-center text-slate-400 space-y-3 border border-slate-800">
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
    window.activeDraftObj = draft;
    renderParliamentaryDraft(draft);
    loadSavedDraftsArchive();

  } catch (err) {
    container.innerHTML = `
      <div class="p-4 sm:p-6 bg-red-500/10 border border-red-500/30 rounded-2xl text-xs text-red-400 space-y-2">
        <div class="font-bold flex items-center gap-2"><i class="fa-solid fa-circle-exclamation"></i> Error Drafting Parliamentary Statement</div>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function renderParliamentaryDraft(draft) {
  const container = document.getElementById('parliament-draft-container');
  if (!container) return;
  window.activeDraftObj = draft;
  
  let annexureRows = '';
  if (draft.annexure_table && draft.annexure_table.length > 0) {
    annexureRows = draft.annexure_table.map(s => {
      const growthStr = (s.total_growth_pct !== null && s.total_growth_pct !== undefined) 
        ? `${s.total_growth_pct > 0 ? '+' : ''}${s.total_growth_pct}%` 
        : 'N/A';
      const growthColor = (s.total_growth_pct !== null && s.total_growth_pct !== undefined)
        ? (s.total_growth_pct >= 0 ? 'text-emerald-400' : 'text-rose-400')
        : 'text-slate-400';
      const cagrStr = (s.cagr_pct !== null && s.cagr_pct !== undefined) ? `${s.cagr_pct}%` : 'N/A';

      return `
        <tr class="hover:bg-slate-800/40">
          <td class="p-3 font-bold text-white">${s.subsidiary}</td>
          <td class="p-3 text-center text-slate-300">${s.start_year_val || 0} MT</td>
          <td class="p-3 text-center font-bold text-emerald-400">${s.end_year_val || 0} MT</td>
          <td class="p-3 text-center ${growthColor} font-semibold">${growthStr}</td>
          <td class="p-3 text-center font-semibold text-slate-300">${cagrStr}</td>
        </tr>
      `;
    }).join('');
  }

  const isApproved = draft.approval_status === 'Approved';

  container.innerHTML = `
    <div id="active-parl-card" class="glass-card rounded-2xl p-4 sm:p-8 shadow-2xl space-y-5 border border-slate-800 relative animate-in fade-in duration-200">
      
      <!-- TOP ACTION & CLOSE BAR -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 text-[10px] sm:text-[11px] font-bold ${isApproved ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'} rounded-full">
              STATUS: ${draft.approval_status.toUpperCase()}
            </span>
            <span class="text-xs text-slate-400 font-medium">${draft.session} • ${draft.house}</span>
          </div>
          <h3 class="text-base sm:text-lg font-bold text-white mt-1.5">${draft.question_no}: ${draft.question_text}</h3>
        </div>
        
        <!-- Action Buttons Group -->
        <div class="flex flex-wrap items-center gap-2">
          ${!isApproved ? (
            currentOfficerRole === 'approver' ? `
              <button onclick="approveDraft('${draft.id}')" class="btn-shimmer px-4 py-2 text-white text-xs font-bold rounded-xl shadow-lg transition flex items-center gap-1.5 hover:scale-[1.02]">
                <i class="fa-solid fa-signature"></i>
                <span>Approve & Sign-Off</span>
              </button>
            ` : `
              <button onclick="toggleOfficerAuth()" class="px-3 py-2 bg-slate-900 border border-amber-500/40 text-amber-300 hover:bg-amber-500/10 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
                <i class="fa-solid fa-lock text-amber-400"></i>
                <span>Sign-Off Locked (Unlock PIN)</span>
              </button>
            `
          ) : `
            <span class="px-3 py-1.5 bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 rounded-xl text-xs font-semibold flex items-center gap-1.5">
              <i class="fa-solid fa-circle-check text-emerald-400"></i>
              <span>Signed by: ${draft.approved_by || 'Under Secretary'}</span>
            </span>
          `}
          
          <button onclick="window.print()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition border border-slate-700">
            <i class="fa-solid fa-print mr-1"></i> Print / PDF
          </button>
          
          <!-- PROMINENT CLOSE / DISMISS BUTTON -->
          <button onclick="closeParliamentaryDraftView()" class="px-4 py-2 bg-rose-950/70 hover:bg-rose-900 border border-rose-500/50 text-rose-300 hover:text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-md">
            <i class="fa-solid fa-xmark text-sm"></i>
            <span>Close Statement</span>
          </button>
        </div>
      </div>

      <!-- Formal Ministry Laid on Table Statement -->
      <div class="bg-slate-950 p-4 sm:p-6 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap shadow-inner relative">
        ${isApproved ? `
          <div class="sm:absolute top-4 right-4 mb-2 sm:mb-0 inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold rounded-lg uppercase tracking-wider">
            <i class="fa-solid fa-stamp text-xs"></i> STATUTORILY APPROVED & SIGNED
          </div>
        ` : ''}
${draft.drafted_response}
      </div>

      <!-- Annexure-I -->
      <div class="space-y-2.5">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <i class="fa-solid fa-table text-emerald-400"></i>
            ANNEXURE-I: SUBSIDIARY-WISE PRODUCTION & CAGR METRICS
          </h4>
          <span class="text-[10px] text-slate-500 font-mono hidden sm:inline">OFFICIAL PARLIAMENTARY RECORD</span>
        </div>
        <div class="table-responsive-wrapper border border-slate-800 rounded-xl bg-slate-950">
          <table class="w-full text-left text-xs border-collapse min-w-[500px]">
            <thead>
              <tr class="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
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

      <!-- BOTTOM CLOSE & DISMISS BAR -->
      <div class="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs">
        <span class="text-slate-500 font-mono text-[11px]">ID: ${draft.id}</span>
        <button onclick="closeParliamentaryDraftView()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold transition border border-slate-700 flex items-center gap-1.5">
          <i class="fa-solid fa-arrow-up"></i>
          <span>Close / Dismiss Statement View</span>
        </button>
      </div>
    </div>
  `;
}

function closeParliamentaryDraftView() {
  const container = document.getElementById('parliament-draft-container');
  if (container) {
    container.innerHTML = '';
    window.activeDraftObj = null;
  }
}

async function approveDraft(draftId) {
  if (currentOfficerRole !== 'approver') {
    toggleOfficerAuth();
    return;
  }

  try {
    const res = await fetch('/api/parliament/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        draft_id: draftId,
        approval_status: 'Approved',
        approved_by: authenticatedOfficerName
      })
    });
    if (!res.ok) throw new Error('Failed to approve draft on server');
    
    alert('Parliamentary Statement officially approved and digitally signed by Under Secretary!');
    
    const draftsRes = await fetch('/api/parliament/list');
    if (draftsRes.ok) {
      const drafts = await draftsRes.json();
      const current = drafts.find(d => d.id === draftId) || drafts[0];
      if (current) renderParliamentaryDraft(current);
    }
    loadSavedDraftsArchive();
  } catch (err) {
    alert('Failed to approve draft: ' + err.message);
  }
}

async function loadSavedDraftsArchive() {
  const container = document.getElementById('parl-archive-container');
  if (!container) return;

  try {
    const res = await fetch('/api/parliament/list');
    if (!res.ok) return;
    const drafts = await res.json();

    if (!drafts || drafts.length === 0) {
      container.innerHTML = `<div class="p-6 bg-slate-900 border border-slate-800 rounded-2xl text-center text-xs text-slate-400">No previous parliamentary drafts archived yet.</div>`;
      return;
    }

    // 1. MOBILE RESPONSIVE CARDS VIEW (Visible on screens < 768px)
    const mobileCardsHtml = `
      <div class="md:hidden space-y-3">
        <div class="p-3 bg-slate-900/90 border border-slate-800 rounded-xl flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
            <i class="fa-solid fa-box-archive text-emerald-400"></i>
            Archived Statements (${drafts.length})
          </h4>
          <span class="text-[10px] text-slate-500 font-mono">Immutable Log</span>
        </div>

        ${drafts.map(d => `
          <div class="glass-card rounded-2xl p-4 border border-slate-800 space-y-3 shadow-lg">
            <div class="flex items-start justify-between gap-2 border-b border-slate-800 pb-2.5">
              <div>
                <h4 class="font-bold text-white text-xs">${d.question_no}</h4>
                <p class="text-[11px] text-slate-400">${d.session} • ${d.house}</p>
              </div>
              <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full flex-shrink-0 ${d.approval_status === 'Approved' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
                ${d.approval_status.toUpperCase()}
              </span>
            </div>

            <p class="text-xs text-slate-300 font-mono bg-slate-950 p-2.5 rounded-xl border border-slate-800/80">
              "${d.question_text}"
            </p>

            <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
              <span>Sign-Off: <strong class="text-slate-300">${d.approved_by ? 'Under Secretary' : 'Pending'}</strong></span>
            </div>

            <!-- Mobile Full-Width Touch Button -->
            <button onclick="viewArchivedDraft('${d.id}')" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow flex items-center justify-center gap-1.5">
              <i class="fa-solid fa-eye"></i>
              <span>View Statement & Annexures</span>
            </button>
          </div>
        `).join('')}
      </div>
    `;

    // 2. DESKTOP RESPONSIVE TABLE VIEW (Visible on tablets and laptops >= 768px)
    const desktopTableHtml = `
      <div class="hidden md:block glass-card rounded-2xl overflow-hidden border border-slate-800 shadow-2xl table-responsive-wrapper">
        <div class="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
          <h4 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <i class="fa-solid fa-box-archive text-emerald-400"></i>
            Archived & Approved Parliamentary Drafts Repository (${drafts.length})
          </h4>
          <span class="text-[10px] text-slate-500 font-mono">Immutable Statutory Log</span>
        </div>
        <table class="w-full text-left text-xs border-collapse min-w-[700px]">
          <thead>
            <tr class="bg-slate-900/50 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
              <th class="p-3.5">Reference / Subject</th>
              <th class="p-3.5 text-center">Session / House</th>
              <th class="p-3.5 text-center">Approval Status</th>
              <th class="p-3.5">Sign-Off Officer</th>
              <th class="p-3.5 text-center">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            ${drafts.map(d => `
              <tr class="hover:bg-slate-800/40">
                <td class="p-3.5">
                  <div class="font-bold text-white">${d.question_no}</div>
                  <div class="text-[11px] text-slate-400 truncate max-w-sm">${d.question_text}</div>
                </td>
                <td class="p-3.5 text-center text-slate-300">${d.session}<br><span class="text-[10px] text-slate-500 font-semibold">${d.house}</span></td>
                <td class="p-3.5 text-center">
                  <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full ${d.approval_status === 'Approved' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
                    ${d.approval_status.toUpperCase()}
                  </span>
                </td>
                <td class="p-3.5 text-slate-300 text-[11px]">${d.approved_by || '<span class="text-slate-500 italic">Pending Approval</span>'}</td>
                <td class="p-3.5 text-center">
                  <button onclick="viewArchivedDraft('${d.id}')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition shadow-sm flex items-center gap-1 mx-auto">
                    <i class="fa-solid fa-eye"></i> View Statement
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = mobileCardsHtml + desktopTableHtml;

  } catch (err) {
    console.error('Error loading parliamentary archive:', err);
  }
}

async function viewArchivedDraft(draftId) {
  try {
    const res = await fetch('/api/parliament/list');
    if (!res.ok) return;
    const drafts = await res.json();
    const draft = drafts.find(d => d.id === draftId);
    if (draft) {
      renderParliamentaryDraft(draft);
      const container = document.getElementById('parliament-draft-container');
      if (container) {
        window.scrollTo({ top: container.offsetTop - 80, behavior: 'smooth' });
      }
    }
  } catch (err) {
    alert('Error loading archived draft: ' + err.message);
  }
}
