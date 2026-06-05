/* train.js */
let allColumns = [];
let lastTrainResult = null;
let coefChart = null;

// Pre-select dataset from sessionStorage
document.addEventListener('DOMContentLoaded', () => {
  const saved = sessionStorage.getItem('selectedDataset');
  if (saved) {
    const sel = document.getElementById('dsSelect');
    // Add as option if upload
    if (!['iris','breast_cancer'].includes(saved)) {
      const opt = document.createElement('option');
      opt.value = saved; opt.textContent = '📁 ' + saved;
      sel.appendChild(opt);
    }
    sel.value = saved;
    onDatasetChange();
  }
  // Auto-generate model name
  document.getElementById('modelName').value =
    'modelo_' + new Date().toISOString().replace(/[-T:\.Z]/g,'').slice(0,14);
});

function onDatasetChange() {
  const val = document.getElementById('dsSelect').value;
  document.getElementById('btnLoadCols').disabled = !val;
  if (val) loadDatasetColumns();
}

async function loadDatasetColumns() {
  const ds = document.getElementById('dsSelect').value;
  if (!ds) { showToast('Selecciona un dataset primero', 'error'); return; }

  showLoading('Cargando columnas...');
  try {
    const info = await apiGet(`/api/dataset/${ds}/info`);
    hideLoading();
    allColumns = info.columns;

    document.getElementById('infoRows').textContent = info.rows;
    document.getElementById('infoCols').textContent = info.cols;
    document.getElementById('dsLoadedInfo').style.display = 'block';

    buildFeatureGrid(info.columns);
    buildTargetSelect(info.columns);

    // Unlock steps
    ['step2','step3','trainBtnRow'].forEach(id => {
      document.getElementById(id).style.opacity = '1';
      document.getElementById(id).style.pointerEvents = 'auto';
    });

    showToast('Dataset cargado correctamente', 'success');
  } catch(e) {
    hideLoading();
    showToast('Error: ' + e.message, 'error');
  }
}

function buildFeatureGrid(cols) {
  const grid = document.getElementById('featureGrid');
  grid.innerHTML = cols.map((c,i) => `
    <label class="feature-checkbox">
      <input type="checkbox" value="${c}" onchange="updateFeatCount()" ${i < cols.length-1 ? 'checked' : ''} />
      ${c}
    </label>`).join('');
  updateFeatCount();
}

function buildTargetSelect(cols) {
  const sel = document.getElementById('targetSelect');
  sel.innerHTML = cols.map((c,i) =>
    `<option value="${c}" ${i === cols.length-1 ? 'selected' : ''}>${c}</option>`).join('');
}

function updateFeatCount() {
  const n = document.querySelectorAll('#featureGrid input:checked').length;
  document.getElementById('featCount').textContent = n + ' seleccionadas';
}

function updateSplit(val) {
  document.getElementById('trainPct').textContent = val + '%';
  document.getElementById('testPct').textContent  = (100-val) + '%';
  document.getElementById('splitTrainBar').style.width = val + '%';
}

function getSelectedFeatures() {
  return [...document.querySelectorAll('#featureGrid input:checked')].map(i => i.value);
}

async function trainModel() {
  const ds       = document.getElementById('dsSelect').value;
  const features = getSelectedFeatures();
  const target   = document.getElementById('targetSelect').value;
  const split    = parseInt(document.getElementById('splitSlider').value);
  const maxIter  = parseInt(document.getElementById('maxIter').value);
  const name     = document.getElementById('modelName').value ||
                   'modelo_' + Date.now();

  if (!ds)              { showToast('Selecciona un dataset', 'error'); return; }
  if (features.length < 1) { showToast('Selecciona al menos 1 feature', 'error'); return; }
  if (!target)          { showToast('Selecciona la variable objetivo', 'error'); return; }
  if (features.includes(target)) { showToast('El target no puede ser un feature', 'error'); return; }

  showLoading('Entrenando modelo... ⏳');

  try {
    const result = await apiPost('/api/train', {
      dataset: ds, features, target,
      test_size: (100-split)/100,
      max_iter: maxIter,
      model_name: name,
    });
    hideLoading();
    lastTrainResult = result;
    showResults(result);
    showToast('¡Modelo entrenado y guardado! 🎉', 'success');
    sessionStorage.setItem('lastModelId', result.model_name);
  } catch(e) {
    hideLoading();
    showToast('Error entrenando: ' + e.message, 'error');
  }
}

function showResults(r) {
  document.getElementById('resultsPanel').style.display = 'block';
  document.getElementById('trainBtnRow').style.opacity = '0.4';
  document.getElementById('trainBtnRow').style.pointerEvents = 'none';

  document.getElementById('resTrainAcc').textContent  = pct(r.train_accuracy);
  document.getElementById('resTestAcc').textContent   = pct(r.test_accuracy);
  document.getElementById('resTrainN').textContent    = r.train_samples;
  document.getElementById('resTestN').textContent     = r.test_samples;
  document.getElementById('resModelName').textContent = r.model_name;

  renderCoefChart(r.coefficients, r.features);
  renderInterceptTable(r.intercepts);

  document.getElementById('resultsPanel').scrollIntoView({ behavior:'smooth' });
}

function renderCoefChart(coefs, features) {
  // Group by first class (or average for multiclass display)
  const cls0 = [...new Set(coefs.map(c => c.class))][0];
  const data  = coefs.filter(c => c.class === cls0);
  const labels = data.map(d => d.feature);
  const values = data.map(d => d.coef);
  const colors = values.map(v => v >= 0 ? 'rgba(26,115,232,.75)' : 'rgba(239,68,68,.7)');

  const ctx = document.getElementById('coefBarChart').getContext('2d');
  if (coefChart) coefChart.destroy();
  coefChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: `Coeficientes (clase: ${cls0})`,
        data: values,
        backgroundColor: colors,
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { labels: { color: 'var(--text-secondary)', font:{size:11} } },
        tooltip: { callbacks: { label: ctx => ` Coef: ${ctx.raw.toFixed(5)}` } }
      },
      scales: {
        x: { ticks:{color:'var(--text-muted)'}, grid:{color:'var(--border)'} },
        y: { ticks:{color:'var(--text-secondary)',font:{size:11}}, grid:{color:'var(--border)'} }
      }
    }
  });
}

function renderInterceptTable(intercepts) {
  const rows = Object.entries(intercepts).map(([cls, val]) => ({
    Clase: cls,
    Intercepto: val.toFixed(6),
    Interpretación: val > 0 ? '↑ Favorece clase' : '↓ Penaliza clase'
  }));
  buildTable(document.getElementById('interceptTable'), rows);
}

function resetForm() {
  document.getElementById('dsSelect').value = '';
  document.getElementById('featureGrid').innerHTML = '<p style="color:var(--text-muted);font-size:.88rem">Carga un dataset primero</p>';
  document.getElementById('dsLoadedInfo').style.display = 'none';
  document.getElementById('resultsPanel').style.display = 'none';
  ['step2','step3','trainBtnRow'].forEach(id => {
    document.getElementById(id).style.opacity = '0.5';
    document.getElementById(id).style.pointerEvents = 'none';
  });
  document.getElementById('trainBtnRow').style.opacity = '0.5';
  document.getElementById('btnLoadCols').disabled = true;
}
