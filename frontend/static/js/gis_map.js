let gisMap = null;
let currentChart = null;

function initGISMap() {
  if (gisMap) {
    setTimeout(() => { gisMap.invalidateSize(); }, 200);
    return;
  }

  gisMap = L.map('gis-map').setView([22.8, 84.5], 6);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 18
  }).addTo(gisMap);

  loadGISData();
}

async function loadGISData() {
  try {
    const res = await fetch('/api/gis/mines');
    const data = await res.json();

    data.features.forEach(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;

      let color = '#22c55e';
      let pulseClass = '';
      if (p.has_conflict) {
        color = '#ef4444';
        pulseClass = 'pulsing-conflict';
      } else if (p.has_anomaly) {
        color = '#f59e0b';
        pulseClass = 'pulsing-marker';
      }

      const marker = L.circleMarker([lat, lng], {
        radius: p.has_conflict ? 10 : (p.has_anomaly ? 9 : 7),
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
        className: pulseClass
      }).addTo(gisMap);

      marker.bindTooltip(`<strong>${p.name}</strong><br><span class="text-xs text-slate-300">${p.subsidiary} • ${p.latest_production} ${p.unit}</span>`, {
        className: 'custom-popup'
      });

      marker.on('click', () => {
        showMineDrawer(p);
      });
    });

  } catch (err) {
    console.error('Failed to load GIS mines:', err);
  }
}

function showMineDrawer(props) {
  const drawer = document.getElementById('gis-drawer-content');
  
  let anomalyHtml = '';
  if (props.has_anomaly && props.anomaly_detail) {
    const a = props.anomaly_detail;
    anomalyHtml = `
      <div class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3 space-y-1">
        <div class="flex items-center justify-between text-amber-400 text-xs font-bold">
          <span><i class="fa-solid fa-triangle-exclamation mr-1"></i> Production Anomaly (${a.fiscal_year})</span>
          <span>${a.deviation_pct > 0 ? '+' : ''}${a.deviation_pct}%</span>
        </div>
        <p class="text-xs text-slate-300">${a.explanation}</p>
        <button onclick="openDocModal('${a.supporting_doc_id}', ${a.supporting_page}, '${a.explanation.replace(/'/g, "\\'")}')" class="text-[11px] text-emerald-400 hover:underline flex items-center gap-1 mt-1 font-semibold">
          <i class="fa-solid fa-file-lines"></i> View Document Note (Page ${a.supporting_page})
        </button>
      </div>
    `;
  }

  let conflictHtml = '';
  if (props.has_conflict && props.conflict_detail) {
    const c = props.conflict_detail;
    conflictHtml = `
      <div class="bg-red-500/10 border border-red-500/30 rounded-xl p-3 space-y-1">
        <div class="flex items-center justify-between text-red-400 text-xs font-bold">
          <span><i class="fa-solid fa-circle-exclamation mr-1"></i> Genuine Data Conflict</span>
          <span>Δ ${c.discrepancy_delta} MT</span>
        </div>
        <p class="text-xs text-slate-300">Conflicting numbers detected across statutory filings. Requires human sign-off.</p>
        <button onclick="switchTab('conflicts')" class="text-[11px] text-red-400 hover:underline font-bold mt-1 block">
          Go to Triage Center →
        </button>
      </div>
    `;
  }

  drawer.innerHTML = `
    <div class="space-y-3">
      <div>
        <span class="px-2 py-0.5 text-[10px] font-bold bg-slate-800 border border-slate-700 text-emerald-400 rounded">${props.subsidiary}</span>
        <h3 class="text-base font-bold text-white mt-1">${props.name}</h3>
        <p class="text-xs text-slate-400">${props.district}, ${props.state} • ${props.mine_type}</p>
      </div>

      <div class="grid grid-cols-2 gap-2 bg-slate-950 p-3 rounded-xl border border-slate-800">
        <div>
          <span class="text-[10px] text-slate-500 uppercase font-semibold">Latest Output</span>
          <p class="text-sm font-bold text-emerald-400">${props.latest_production} ${props.unit}</p>
        </div>
        <div>
          <span class="text-[10px] text-slate-500 uppercase font-semibold">Fiscal Year</span>
          <p class="text-sm font-bold text-slate-200">${props.latest_fiscal_year}</p>
        </div>
      </div>

      ${anomalyHtml}
      ${conflictHtml}

      <div>
        <h4 class="text-xs font-semibold text-slate-300 mb-2">Historical Production Trajectory</h4>
        <div class="bg-slate-950 p-2 rounded-xl border border-slate-800 h-44">
          <canvas id="mine-history-chart"></canvas>
        </div>
      </div>

      <button onclick="openDocModal('DOC001_ANNUAL_REPORT_2024', 17, '${props.name} produced ${props.latest_production} ${props.unit} of coal.')" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition border border-slate-700 flex items-center justify-center gap-2">
        <i class="fa-solid fa-file-certificate text-emerald-400"></i>
        <span>Inspect Source Bounding Box</span>
      </button>
    </div>
  `;

  const years = Object.keys(props.yearly_production || {});
  const values = Object.values(props.yearly_production || {});
  
  const ctx = document.getElementById('mine-history-chart');
  if (ctx && years.length > 0) {
    if (currentChart) currentChart.destroy();
    currentChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: years,
        datasets: [{
          label: 'Production (MT)',
          data: values,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: '#10b981'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { display: false } },
          y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: '#1e293b' } }
        }
      }
    });
  }
}
