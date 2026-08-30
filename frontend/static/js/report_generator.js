async function generateReport() {
  const startYear = document.getElementById('report-start-year').value;
  const endYear = document.getElementById('report-end-year').value;
  const subsidiary = document.getElementById('report-subsidiary').value;
  const container = document.getElementById('report-preview-container');

  container.innerHTML = `
    <div class="bg-coal-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 space-y-3">
      <i class="fa-solid fa-circle-notch fa-spin text-emerald-400 text-3xl"></i>
      <p class="text-xs">Aggregating multi-source factual records, computing deterministic CAGR, and compiling all 6 statutory report sections...</p>
    </div>
  `;

  try {
    let url = `/api/reports/generate?start_year=${encodeURIComponent(startYear)}&end_year=${encodeURIComponent(endYear)}`;
    if (subsidiary) url += `&subsidiary=${encodeURIComponent(subsidiary)}`;

    const res = await fetch(url);
    const rep = await res.json();

    // Section 2: Production & CAGR Matrix
    let matrixHtml = '';
    const matrixSec = rep.sections.find(s => s.table_type === 'subsidiary_matrix');
    if (matrixSec && matrixSec.data) {
      matrixHtml = `
        <div class="overflow-x-auto my-3">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
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
        <div class="overflow-x-auto my-3">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
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
        <div class="overflow-x-auto my-3">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                <th class="p-3">State</th>
                <th class="p-3 text-center">Estimated Reserves (BT)</th>
                <th class="p-3 text-center">Latest Output (MT)</th>
                <th class="p-3 text-center">National Share (%)</th>
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
        <div class="overflow-x-auto my-3">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
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
        <div class="overflow-x-auto my-3">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                <th class="p-3">Mine Entity</th>
                <th class="p-3 text-center">Classification</th>
                <th class="p-3 text-center">Variance (Δ)</th>
                <th class="p-3 text-center">Audit Status</th>
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
      <div class="bg-coal-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-5 gap-3">
          <div>
            <span class="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded">CONFIDENTIAL STATUTORY AUDIT</span>
            <h3 class="text-xl font-bold text-white mt-1">${rep.title}</h3>
            <p class="text-xs text-slate-400">Generated: ${rep.generated_at} • Parameters: ${rep.parameters.subsidiary} (${rep.parameters.start_year} to ${rep.parameters.end_year})</p>
          </div>
          <div class="flex space-x-2">
            <button onclick="window.print()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs rounded-lg font-medium transition">
              <i class="fa-solid fa-print mr-1"></i> Print / PDF
            </button>
          </div>
        </div>

        <!-- 4 Key Summary KPI Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Start Output (${startYear})</span>
            <p class="text-lg font-bold text-slate-200 mt-1">${rep.summary_metrics.start_total_mt.toFixed(2)} MT</p>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">End Output (${endYear})</span>
            <p class="text-lg font-bold text-emerald-400 mt-1">${rep.summary_metrics.end_total_mt.toFixed(2)} MT</p>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Overall Growth</span>
            <p class="text-lg font-bold text-emerald-400 mt-1">+${rep.summary_metrics.growth_pct}%</p>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Total Overburden</span>
            <p class="text-lg font-bold text-teal-400 mt-1">${(rep.summary_metrics.total_ob_mcum || 0).toFixed(1)} MCuM</p>
          </div>
        </div>

        <!-- All 6 Sections Rendered Sequentially -->
        <div class="space-y-6 text-xs text-slate-300 leading-relaxed">
          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-file-lines text-emerald-400"></i> 1. Executive Summary</h4>
            <p>${rep.sections[0].content}</p>
          </div>

          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-table text-emerald-400"></i> 2. Subsidiary Production & CAGR Matrix</h4>
            ${matrixHtml}
          </div>

          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-mountain text-emerald-400"></i> 3. Geotechnical & Overburden Removal (MCuM) Summary</h4>
            ${obHtml}
          </div>

          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-map-location-dot text-emerald-400"></i> 4. State-wise Resource & Production Allocation</h4>
            ${stateHtml}
          </div>

          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-triangle-exclamation text-amber-400"></i> 5. Detected Operational Anomalies & Root Causes</h4>
            ${anomHtml}
          </div>

          <div class="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-2">
            <h4 class="text-sm font-bold text-white flex items-center gap-2"><i class="fa-solid fa-scale-balanced text-emerald-400"></i> 6. Data Consistency & Conflict Resolution Audit Trail</h4>
            ${confHtml}
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400">Failed to generate report: ${err.message}</div>`;
  }
}
