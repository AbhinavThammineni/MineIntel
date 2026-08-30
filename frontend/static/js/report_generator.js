// Automated Reports Generator with Responsive Mobile Tables

async function generateReport() {
  const startYear = document.getElementById('report-start-year')?.value || '2021-22';
  const endYear = document.getElementById('report-end-year')?.value || '2024-25';
  const subsidiary = document.getElementById('report-subsidiary')?.value || '';
  const container = document.getElementById('report-preview-container');

  if (!container) return;

  container.innerHTML = `
    <div class="glass-card rounded-2xl p-12 text-center text-slate-400 space-y-3 border border-slate-800">
      <i class="fa-solid fa-circle-notch fa-spin text-emerald-400 text-3xl"></i>
      <p class="text-xs">Aggregating multi-source factual records, computing deterministic CAGR, and compiling all 6 statutory report sections...</p>
    </div>
  `;

  try {
    let url = `/api/reports/generate?start_year=${encodeURIComponent(startYear)}&end_year=${encodeURIComponent(endYear)}`;
    if (subsidiary) url += `&subsidiary=${encodeURIComponent(subsidiary)}`;

    const res = await fetch(url);
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Server returned error (${res.status}): ${errText}`);
    }

    const rep = await res.json();

    // Section 2: Production & CAGR Matrix
    let matrixHtml = '';
    const matrixSec = rep.sections.find(s => s.table_type === 'subsidiary_matrix');
    if (matrixSec && matrixSec.data) {
      matrixHtml = `
        <div class="table-responsive-wrapper my-2">
          <table class="w-full text-left text-xs border-collapse min-w-[550px]">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th class="p-3">Subsidiary</th>
                <th class="p-3 text-center">Start (${startYear})</th>
                <th class="p-3 text-center">End (${endYear})</th>
                <th class="p-3 text-center">Total Growth</th>
                <th class="p-3 text-center">CAGR (%)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
              ${matrixSec.data.map(sub => `
                <tr class="hover:bg-slate-800/40">
                  <td class="p-3 font-bold text-white">${sub.subsidiary}</td>
                  <td class="p-3 text-center">${sub.start_year_val} MT</td>
                  <td class="p-3 text-center font-bold text-emerald-400">${sub.end_year_val} MT</td>
                  <td class="p-3 text-center ${sub.total_growth_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'} font-semibold">${sub.total_growth_pct > 0 ? '+' : ''}${sub.total_growth_pct || 0}%</td>
                  <td class="p-3 text-center font-semibold text-slate-300">${sub.cagr_pct ? `${sub.cagr_pct}%` : 'N/A'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Section 3: Overburden Removal Matrix (MCuM)
    let obHtml = '';
    const obSec = rep.sections.find(s => s.table_type === 'overburden_matrix');
    if (obSec && obSec.data && obSec.data.length > 0) {
      obHtml = `
        <div class="table-responsive-wrapper my-2">
          <table class="w-full text-left text-xs border-collapse min-w-[550px]">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th class="p-3">Mine Name</th>
                <th class="p-3 text-center">Subsidiary</th>
                <th class="p-3 text-center">Period</th>
                <th class="p-3 text-center">Volume (MCuM)</th>
                <th class="p-3">Operational Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
              ${obSec.data.map(ob => `
                <tr class="hover:bg-slate-800/40">
                  <td class="p-3 font-bold text-white">${ob.mine_name}</td>
                  <td class="p-3 text-center text-slate-300">${ob.subsidiary}</td>
                  <td class="p-3 text-center text-slate-400">${ob.fiscal_year}</td>
                  <td class="p-3 text-center font-bold text-emerald-400">${ob.normalized_value} MCuM</td>
                  <td class="p-3 text-slate-300 text-[11px]">${ob.normalized_value >= 50 ? 'Accelerated Stripping' : 'Normal Bench Advance'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Section 4: State-wise Resource Allocation
    let stateHtml = '';
    const stateSec = rep.sections.find(s => s.table_type === 'state_allocation');
    if (stateSec && stateSec.data && stateSec.data.length > 0) {
      stateHtml = `
        <div class="table-responsive-wrapper my-2">
          <table class="w-full text-left text-xs border-collapse min-w-[500px]">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th class="p-3">State</th>
                <th class="p-3 text-center">Reserves (BT)</th>
                <th class="p-3 text-center">Latest Output (MT)</th>
                <th class="p-3 text-center">Share (%)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
              ${stateSec.data.map(st => `
                <tr class="hover:bg-slate-800/40">
                  <td class="p-3 font-bold text-white">${st.state}</td>
                  <td class="p-3 text-center font-semibold text-slate-300">${st.reserves_bt} BT</td>
                  <td class="p-3 text-center font-bold text-emerald-400">${st.latest_production} MT</td>
                  <td class="p-3 text-center text-slate-300 font-medium">${st.share_pct}%</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Section 5: Anomalies Table
    let anomHtml = '';
    const anomSec = rep.sections.find(s => s.table_type === 'anomalies_list');
    if (anomSec && anomSec.data && anomSec.data.length > 0) {
      anomHtml = `
        <div class="table-responsive-wrapper my-2">
          <table class="w-full text-left text-xs border-collapse min-w-[550px]">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th class="p-3">Mine Project</th>
                <th class="p-3 text-center">Subsidiary</th>
                <th class="p-3 text-center">Period</th>
                <th class="p-3 text-center">Deviation</th>
                <th class="p-3">Operational Root Cause</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
              ${anomSec.data.map(a => `
                <tr class="hover:bg-slate-800/40">
                  <td class="p-3 font-bold text-white">${a.mine_name}</td>
                  <td class="p-3 text-center text-slate-300">${a.subsidiary}</td>
                  <td class="p-3 text-center text-slate-400">${a.fiscal_year}</td>
                  <td class="p-3 text-center font-bold ${a.deviation_pct > 0 ? 'text-amber-400' : 'text-rose-400'}">${a.deviation_pct > 0 ? '+' : ''}${a.deviation_pct}%</td>
                  <td class="p-3 text-slate-300 text-[11px]">${a.explanation}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Section 6: Conflict & Supersession Log
    let confHtml = '';
    const confSec = rep.sections.find(s => s.table_type === 'conflict_audit');
    if (confSec && confSec.data && confSec.data.length > 0) {
      confHtml = `
        <div class="table-responsive-wrapper my-2">
          <table class="w-full text-left text-xs border-collapse min-w-[550px]">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th class="p-3">Mine Entity</th>
                <th class="p-3 text-center">Type</th>
                <th class="p-3 text-center">Delta (Δ)</th>
                <th class="p-3 text-center">Status</th>
                <th class="p-3">Resolution & Audit Log</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800 text-slate-200">
              ${confSec.data.map(c => `
                <tr class="hover:bg-slate-800/40">
                  <td class="p-3 font-bold text-white">${c.mine_name}</td>
                  <td class="p-3 text-center text-slate-300 text-[11px]">${c.conflict_type === 'superseded_discrepancy' ? 'Supersession' : 'Genuine Conflict'}</td>
                  <td class="p-3 text-center font-mono text-slate-300">${c.discrepancy_delta} MT</td>
                  <td class="p-3 text-center font-bold ${c.status === 'superseded' ? 'text-emerald-400' : 'text-amber-400'}">${c.status.toUpperCase()}</td>
                  <td class="p-3 text-slate-300 text-[11px]">${c.resolution_notes}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="glass-card rounded-2xl p-4 sm:p-8 shadow-2xl space-y-5 border border-slate-800">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-2">
          <div>
            <span class="px-2 py-0.5 text-[9px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded">STATUTORY AUDIT</span>
            <h3 class="text-base sm:text-xl font-bold text-white mt-1">${rep.title}</h3>
            <p class="text-[11px] text-slate-400">${rep.parameters.subsidiary} (${rep.parameters.start_year} to ${rep.parameters.end_year})</p>
          </div>
          <button onclick="window.print()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs rounded-lg font-medium transition self-start sm:self-auto">
            <i class="fa-solid fa-print mr-1"></i> Print / PDF
          </button>
        </div>

        <!-- 4 Summary KPI Cards (Responsive Grid) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-4">
          <div class="bg-slate-950 p-3 sm:p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Start (${startYear})</span>
            <p class="text-base sm:text-lg font-bold text-slate-200 mt-1">${rep.summary_metrics.start_total_mt.toFixed(1)} MT</p>
          </div>
          <div class="bg-slate-950 p-3 sm:p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">End (${endYear})</span>
            <p class="text-base sm:text-lg font-bold text-emerald-400 mt-1">${rep.summary_metrics.end_total_mt.toFixed(1)} MT</p>
          </div>
          <div class="bg-slate-950 p-3 sm:p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Growth</span>
            <p class="text-base sm:text-lg font-bold text-emerald-400 mt-1">+${rep.summary_metrics.growth_pct}%</p>
          </div>
          <div class="bg-slate-950 p-3 sm:p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Overburden</span>
            <p class="text-base sm:text-lg font-bold text-teal-400 mt-1">${(rep.summary_metrics.total_ob_mcum || 0).toFixed(1)} MCuM</p>
          </div>
        </div>

        <!-- All 6 Sections Rendered Sequentially -->
        <div class="space-y-5 text-xs text-slate-300 leading-relaxed">
          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-file-lines text-emerald-400"></i> 1. Executive Summary</h4>
            <p>${rep.sections[0].content}</p>
          </div>

          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-table text-emerald-400"></i> 2. Subsidiary Production & CAGR Matrix</h4>
              <span class="text-[9px] text-slate-500 sm:hidden">Swipe table ➔</span>
            </div>
            ${matrixHtml}
          </div>

          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-mountain text-emerald-400"></i> 3. Overburden Removal (MCuM)</h4>
              <span class="text-[9px] text-slate-500 sm:hidden">Swipe table ➔</span>
            </div>
            ${obHtml}
          </div>

          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-map-location-dot text-emerald-400"></i> 4. State-wise Allocation</h4>
              <span class="text-[9px] text-slate-500 sm:hidden">Swipe table ➔</span>
            </div>
            ${stateHtml}
          </div>

          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-triangle-exclamation text-amber-400"></i> 5. Operational Anomalies & Root Causes</h4>
              <span class="text-[9px] text-slate-500 sm:hidden">Swipe table ➔</span>
            </div>
            ${anomHtml}
          </div>

          <div class="bg-slate-950 p-4 sm:p-5 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs sm:text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-scale-balanced text-emerald-400"></i> 6. Data Consistency & Conflict Audit Log</h4>
              <span class="text-[9px] text-slate-500 sm:hidden">Swipe table ➔</span>
            </div>
            ${confHtml}
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="p-4 sm:p-6 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400">Failed to generate report: ${err.message}</div>`;
  }
}
