/* dashboard.js */
let currentDataset = null;

async function loadQuickStats() {
  try {
    const [dsData, modData] = await Promise.all([
      apiGet('/api/datasets'),
      apiGet('/api/models'),
    ]);
    document.getElementById('statDatasets').textContent = dsData.datasets.length;
    document.getElementById('statModels').textContent   = modData.models.length;
    renderModelsList(modData.models);
  } catch (e) {
    console.warn('API no disponible:', e.message);
    document.getElementById('statDatasets').textContent = '—';
    document.getElementById('statModels').textContent   = '—';
    document.getElementById('modelsList').innerHTML =
      `<div class="text-center py-3" style="color:var(--text-muted)">
         <i class="bi bi-wifi-off" style="font-size:2rem"></i>
         <p class="mt-2">Conecta el backend Flask para ver los modelos.</p>
         <code style="font-size:.8rem">python app.py</code>
       </div>`;
  }
}

async function selectDataset(name, sideEl) {
  currentDataset = name;

  // Active tabs
  document.querySelectorAll('.ds-tab').forEach(t => t.classList.remove('active'));
  const tab = document.getElementById('tab-' + name);
  if (tab) tab.classList.add('active');

  // Sidebar active
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
  if (sideEl) sideEl.classList.add('active');

  document.getElementById('dsPlaceholder').style.display = 'none';
  document.getElementById('dsInfoPanel').style.display   = 'block';

  // Store for train page
  sessionStorage.setItem('selectedDataset', name);

  showLoading('Cargando dataset...');
  try {
    const info = await apiGet(`/api/dataset/${name}/info`);
    hideLoading();

    document.getElementById('dsName').textContent   = name;
    document.getElementById('statRows').textContent = info.rows;
    document.getElementById('statCols').textContent = info.cols;

    // Stat cards
    const statsHtml = [
      { icon:'bi-grid',           label:'Filas',    value: info.rows,                   color:'blue'   },
      { icon:'bi-list-columns',   label:'Columnas', value: info.cols,                   color:'cyan'   },
      { icon:'bi-x-circle',       label:'Nulos',    value: Object.values(info.nulls).reduce((a,b)=>a+b,0), color:'orange'},
      { icon:'bi-tag',            label:'Target col',value: info.columns[info.columns.length-1], color:'green' },
    ].map(s => `
      <div class="col-6 col-md-3">
        <div class="metric-card">
          <div class="card-icon card-icon-${s.color} mx-auto mb-1" style="width:40px;height:40px;font-size:1rem">
            <i class="bi ${s.icon}"></i>
          </div>
          <div class="metric-label">${s.label}</div>
          <div class="metric-value" style="font-size:1.5rem">${s.value}</div>
        </div>
      </div>`).join('');
    document.getElementById('dsStatCards').innerHTML = statsHtml;

    // Preview table
    buildTable(document.getElementById('previewTable'), info.preview);

  } catch(e) {
    hideLoading();
    showToast('Error al cargar dataset: ' + e.message, 'error');
  }
}

async function uploadCSV(input) {
  const file = input.files[0];
  if (!file) return;

  const barWrap = document.getElementById('uploadBarWrap');
  const barFill = document.getElementById('uploadBarFill');
  const msg     = document.getElementById('uploadMsg');

  barWrap.style.display = 'block';
  barFill.style.width   = '30%';
  msg.textContent = `Subiendo ${file.name}...`;

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await apiUpload('/api/upload', fd);
    barFill.style.width = '100%';
    msg.textContent = `✅ ${file.name} subido correctamente`;
    showToast('Dataset subido: ' + file.name, 'success');

    const dsName = file.name.replace('.csv','');
    sessionStorage.setItem('selectedDataset', dsName);

    // Show upload tab
    document.getElementById('tab-upload-card').style.display = 'block';
    document.getElementById('uploadTabName').textContent = dsName;
    document.getElementById('uploadTabDesc').textContent = 'Dataset personalizado';

    setTimeout(() => { barWrap.style.display = 'none'; barFill.style.width = '0%'; }, 2000);
    selectDataset(dsName, null);
  } catch(e) {
    barFill.style.background = 'var(--danger)';
    msg.textContent = '❌ Error: ' + e.message;
    showToast('Error al subir: ' + e.message, 'error');
  }
}

function renderModelsList(models) {
  const el = document.getElementById('modelsList');
  if (!models || models.length === 0) {
    el.innerHTML = `<div class="text-center py-4" style="color:var(--text-muted)">
      <i class="bi bi-inbox" style="font-size:2.5rem"></i>
      <p class="mt-2">No hay modelos entrenados aún.</p>
      <a href="train.html" class="btn-primary-custom mt-1"><i class="bi bi-cpu"></i> Entrenar primer modelo</a>
    </div>`;
    return;
  }
  const rows = models.map(m => ({
    ID: m.id,
    Nombre: m.name,
    Dataset: m.dataset,
    Target: m.target,
    Accuracy: (m.accuracy * 100).toFixed(2) + '%',
    Creado: m.created_at ? m.created_at.split('T')[0] : '—',
  }));
  buildTable(el, rows);
}

// Dropzone drag-and-drop
document.addEventListener('DOMContentLoaded', () => {
  loadQuickStats();

  const dz = document.getElementById('dropzone');
  dz.addEventListener('dragover',  e => { e.preventDefault(); dz.classList.add('drag-over'); });
  dz.addEventListener('dragleave', ()  => dz.classList.remove('drag-over'));
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      const dt = new DataTransfer();
      dt.items.add(file);
      document.getElementById('csvFile').files = dt.files;
      uploadCSV(document.getElementById('csvFile'));
    } else {
      showToast('Solo se aceptan archivos .csv', 'error');
    }
  });
});
