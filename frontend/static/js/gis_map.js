// High-Speed Geospatial Leaflet Map Controller for Indian Coalfields
// 100% Free OpenStreetMap Global Tiles (Zero API Key, Zero Watermarks)

window.mineGisMap = null;
let currentChart = null;

function onGisTabActivated() {
  const mapEl = document.getElementById('gis-map');
  if (!mapEl) return;

  if (!window.mineGisMap) {
    initGisMap();
  }

  // Multi-pass size invalidation to handle browser layout paint timing
  [50, 150, 300, 500].forEach(delay => {
    setTimeout(() => {
      if (window.mineGisMap) {
        window.mineGisMap.invalidateSize(true);
      }
    }, delay);
  });
}

function initGisMap() {
  const mapEl = document.getElementById('gis-map');
  if (!mapEl || window.mineGisMap) return;

  try {
    // Center on Central Indian Coalfields (Ranchi / Bilaspur / Dhanbad region)
    window.mineGisMap = L.map('gis-map', {
      zoomControl: true,
      fadeAnimation: true,
      zoomAnimation: true
    }).setView([23.4, 84.5], 6);

    // 100% Free OpenStreetMap Global CDN (No API keys, Zero Watermarks)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
      subdomains: ['a', 'b', 'c']
    }).addTo(window.mineGisMap);

    loadMinesOnMap();
  } catch (err) {
    console.error('Error initializing Leaflet map:', err);
  }
}

async function loadMinesOnMap() {
  if (!window.mineGisMap) return;

  try {
    const res = await fetch('/api/gis/mines');
    if (!res.ok) return;
    const rawData = await res.json();
    
    // Handle both direct array and FeatureCollection formats
    const mines = Array.isArray(rawData) ? rawData : (rawData.features ? rawData.features.map(f => ({
      ...f.properties,
      latitude: f.geometry.coordinates[1],
      longitude: f.geometry.coordinates[0]
    })) : []);

    mines.forEach(mine => {
      let markerColor = '#10b981'; // Emerald (Normal)
      let radius = 10;

      if (mine.has_conflict) {
        markerColor = '#ef4444'; // Red (Conflict)
        radius = 13;
      } else if (mine.has_anomaly) {
        markerColor = '#f59e0b'; // Amber (Anomaly)
        radius = 12;
      }

      const lat = parseFloat(mine.latitude || mine.lat || 23.0);
      const lng = parseFloat(mine.longitude || mine.lng || 84.0);

      const circle = L.circleMarker([lat, lng], {
        color: '#ffffff',
        fillColor: markerColor,
        fillOpacity: 0.9,
        radius: radius,
        weight: 2
      }).addTo(window.mineGisMap);

      circle.bindTooltip(`
        <div class="font-sans text-xs">
          <strong class="text-white">${mine.name}</strong><br>
          <span class="text-emerald-400 font-semibold">${mine.subsidiary}</span> • ${mine.state}<br>
          <span class="text-slate-300">Output: ${mine.latest_production || 0} MT</span>
        </div>
      `, {
        className: 'custom-popup'
      });

      circle.on('click', () => {
        selectMine(mine.code);
      });
    });

    // Auto-select Gevra by default for showcase
    if (mines.length > 0) {
      const defaultMine = mines.find(m => m.code === 'MINE_GEVRA') || mines[0];
      selectMine(defaultMine.code);
    }
  } catch (err) {
    console.error('Error loading mines on map:', err);
  }
}

async function selectMine(mineCode) {
  const drawerContent = document.getElementById('gis-drawer-content');
  if (!drawerContent) return;

  drawerContent.innerHTML = `
    <div class="py-12 text-center text-slate-400 space-y-2">
      <i class="fa-solid fa-circle-notch fa-spin text-emerald-400 text-2xl"></i>
      <p class="text-xs">Loading factual telemetry and historical records...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/gis/mine/${mineCode}`);
    if (!res.ok) {
      throw new Error('Failed to fetch mine details');
    }
    const data = await res.json();
    const mine = data.mine;
    const facts = data.facts || [];
    const obFacts = data.overburden_facts || [];
    const anomalies = data.anomalies || [];
    const conflicts = data.conflicts || [];

    const latestFact = facts.length > 0 ? facts[facts.length - 1] : null;
    const latestOb = obFacts.length > 0 ? obFacts[obFacts.length - 1] : null;

    let anomalyBadge = '';
    if (anomalies.length > 0) {
      const a = anomalies[0];
      anomalyBadge = `
        <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs space-y-1">
          <div class="font-bold text-amber-400 flex items-center gap-1.5">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <span>Statistical Anomaly: ${a.deviation_pct > 0 ? '+' : ''}${a.deviation_pct}%</span>
          </div>
          <p class="text-slate-300 text-[11px] leading-relaxed">${a.explanation}</p>
        </div>
      `;
    }

    let conflictBadge = '';
    if (conflicts.length > 0) {
      const c = conflicts[0];
      conflictBadge = `
        <div class="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-xs space-y-1">
          <div class="font-bold text-red-400 flex items-center gap-1.5">
            <i class="fa-solid fa-scale-unbalanced"></i>
            <span>Data Discrepancy (Delta: ${c.discrepancy_delta} MT)</span>
          </div>
          <p class="text-slate-300 text-[11px] leading-relaxed">${c.resolution_notes}</p>
        </div>
      `;
    }

    drawerContent.innerHTML = `
      <div class="space-y-4 animate-in fade-in duration-200">
        <div class="border-b border-slate-800 pb-3">
          <div class="flex items-center justify-between">
            <span class="px-2.5 py-0.5 text-[10px] font-bold bg-slate-800 text-emerald-400 border border-slate-700 rounded-full">${mine.subsidiary}</span>
            <span class="text-xs text-slate-400">${mine.district}, ${mine.state}</span>
          </div>
          <h3 class="text-base font-bold text-white mt-1.5">${mine.name}</h3>
          <p class="text-[11px] text-slate-500 font-mono">Code: ${mine.code} • Lat: ${mine.latitude ? mine.latitude.toFixed(3) : 23.0}, Lng: ${mine.longitude ? mine.longitude.toFixed(3) : 84.0}</p>
        </div>

        <!-- 2 KPI Mini Cards -->
        <div class="grid grid-cols-2 gap-2.5">
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Latest Output</span>
            <p class="text-base font-bold text-emerald-400 mt-0.5">${latestFact ? `${latestFact.normalized_value} MT` : 'N/A'}</p>
            <span class="text-[9px] text-slate-500">${latestFact ? latestFact.fiscal_year : ''}</span>
          </div>
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span class="text-[10px] text-slate-500 uppercase font-semibold">Overburden Vol</span>
            <p class="text-base font-bold text-teal-400 mt-0.5">${latestOb ? `${latestOb.normalized_value} MCuM` : 'N/A'}</p>
            <span class="text-[9px] text-slate-500">${latestOb ? latestOb.fiscal_year : 'Stripping'}</span>
          </div>
        </div>

        ${anomalyBadge}
        ${conflictBadge}

        <!-- Mini Production Trajectory Chart -->
        <div class="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2">
          <span class="text-[11px] font-bold text-slate-300 flex items-center gap-1.5">
            <i class="fa-solid fa-chart-area text-emerald-400"></i> Production Trajectory
          </span>
          <div class="h-36">
            <canvas id="mine-history-chart"></canvas>
          </div>
        </div>

        <!-- Verified Citation & Bounding Box Action -->
        ${latestFact ? `
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between text-[11px]">
              <span class="font-bold text-emerald-400"><i class="fa-solid fa-file-pdf mr-1"></i> ${latestFact.doc_id}</span>
              <span class="text-slate-400">Page ${latestFact.page_number}</span>
            </div>
            <button onclick="openDocModal('${latestFact.doc_id}', ${latestFact.page_number}, '${encodeURIComponent(JSON.stringify(latestFact.bbox || {}))}', '${encodeURIComponent(latestFact.raw_text || '')}')" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 border border-slate-700 shadow-sm">
              <i class="fa-solid fa-magnifying-glass text-emerald-400"></i>
              <span>Inspect Bounding Box</span>
            </button>
          </div>
        ` : ''}
      </div>
    `;

    // Render Chart.js
    if (facts.length > 0) {
      setTimeout(() => {
        const ctx = document.getElementById('mine-history-chart');
        if (ctx) {
          if (currentChart) currentChart.destroy();
          const labels = facts.map(f => f.fiscal_year);
          const values = facts.map(f => f.normalized_value);

          currentChart = new Chart(ctx, {
            type: 'line',
            data: {
              labels: labels,
              datasets: [{
                label: 'Output (MT)',
                data: values,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                fill: true,
                tension: 0.35,
                borderWidth: 2,
                pointBackgroundColor: '#10b981',
                pointRadius: 4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: {
                x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { display: false } },
                y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' } }
              }
            }
          });
        }
      }, 100);
    }

    // Auto scroll down to drawer on mobile
    if (window.innerWidth < 1024) {
      const drawer = document.getElementById('gis-drawer');
      if (drawer) {
        drawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }

  } catch (err) {
    drawerContent.innerHTML = `<div class="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400">Failed to load mine details. Please retry.</div>`;
  }
}
