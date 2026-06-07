/* predict.js */
let currentModel  = null;
let probChartInst = null;
let predHistory   = [];
let datasetStats  = null;
let datasetDtypes = null;

document.addEventListener('DOMContentLoaded', loadModels);

async function loadModels() {
  try {
    const data = await apiGet('/api/models');
    const sel  = document.getElementById('modelSelect');
    if (!data.models.length) {
      sel.innerHTML = '<option value="">-- Sin modelos entrenados --</option>';
      return;
    }
    sel.innerHTML = '<option value="">-- Seleccionar modelo --</option>' +
      data.models.map(m =>
        `<option value="${m.id}" data-model='${JSON.stringify(m)}'>${m.name} · ${m.dataset} · Acc ${(m.accuracy*100).toFixed(1)}%</option>`
      ).join('');
  } catch(e) {
    document.getElementById('modelSelect').innerHTML =
      '<option value="">-- Backend no disponible --</option>';
  }
}

function onModelChange() {
  const sel = document.getElementById('modelSelect');
  const opt = sel.options[sel.selectedIndex];
  document.getElementById('btnLoadFeats').disabled = !sel.value;

  if (!sel.value) return;

  try {
    currentModel = JSON.parse(opt.getAttribute('data-model'));
    document.getElementById('modelInfoBadges').style.display = 'block';
    document.getElementById('modelBadges').innerHTML = `
      <span class="badge-custom badge-blue"><i class="bi bi-database"></i> ${currentModel.dataset}</span>
      <span class="badge-custom badge-green"><i class="bi bi-tag"></i> Target: ${currentModel.target}</span>
      <span class="badge-custom badge-purple"><i class="bi bi-list-columns"></i> ${currentModel.features.length} features</span>
    `;
    loadModelFeatures();
  } catch(e) { console.warn(e); }
}

async function loadModelFeatures() {
  const sel = document.getElementById('modelSelect');
  if (!sel.value || !currentModel) { showToast('Selecciona un modelo', 'error'); return; }

  // Try to get dataset stats for ranges
  try {
    const info = await apiGet(`/api/dataset/${currentModel.dataset}/info`);
    datasetStats = info.numeric_stats;
    datasetDtypes = info.dtypes;
  } catch(e) { datasetStats = null; datasetDtypes = null; }

  buildPredForm(currentModel.features);
  document.getElementById('predFormSection').style.display = 'block';
  document.getElementById('predPlaceholder').style.display = 'none';
  document.getElementById('predResultSection').style.display = 'none';
  document.getElementById('formModelName').textContent = currentModel.name;
}

function buildPredForm(features) {
  const grid = document.getElementById('predInputGrid');
  grid.innerHTML = features.map(f => {
    let min = '', max = '', step = '0.01', placeholder = '';
    let isNumeric = true;
    if (datasetDtypes && datasetDtypes[f] === 'object') {
       isNumeric = false;
    }
    
    if (isNumeric && datasetStats && datasetStats.min && datasetStats.min[f] != null) {
      min = parseFloat(datasetStats.min[f]).toFixed(2);
      max = parseFloat(datasetStats.max[f]).toFixed(2);
      const mean = parseFloat(datasetStats.mean[f]).toFixed(2);
      placeholder = mean;
    }
    
    let inputHtml = '';
    if (isNumeric) {
        if (!placeholder) placeholder = '0.0';
        inputHtml = `<input type="number" id="feat_${f.replace(/[^a-z0-9]/gi,'_')}"
               class="form-control-custom pred-input"
               data-feature="${f}"
               data-type="numeric"
               step="${step}"
               placeholder="${placeholder}"
               value="${placeholder}"
               ${min ? `min="${min}"` : ''} ${max ? `max="${max}"` : ''} />`;
    } else {
        inputHtml = `<input type="text" id="feat_${f.replace(/[^a-z0-9]/gi,'_')}"
               class="form-control-custom pred-input"
               data-feature="${f}"
               data-type="categorical"
               placeholder="Categoría..."
               value="" />`;
    }

    return `
      <div class="col-md-6 col-lg-4">
        <label class="form-label-custom">${f}
          ${min && max ? `<small style="color:var(--text-muted);font-weight:400">[${min} – ${max}]</small>` : ''}
        </label>
        ${inputHtml}
      </div>`;
  }).join('');
}

async function makePrediction() {
  if (!currentModel) { showToast('Selecciona un modelo primero', 'error'); return; }

  const inputs = {};
  let valid = true;
  document.querySelectorAll('.pred-input').forEach(inp => {
    const feat = inp.getAttribute('data-feature');
    const isCat = inp.getAttribute('data-type') === 'categorical';
    
    if (isCat) {
        const val = inp.value.trim();
        if (!val) { valid = false; inp.style.borderColor = 'var(--danger)'; }
        else { inp.style.borderColor = ''; inputs[feat] = val; }
    } else {
        const val = parseFloat(inp.value);
        if (isNaN(val)) { valid = false; inp.style.borderColor = 'var(--danger)'; }
        else { inp.style.borderColor = ''; inputs[feat] = val; }
    }
  });
  if (!valid) { showToast('Completa todos los campos correctamente', 'error'); return; }

  showLoading('Calculando predicción...');
  try {
    const r = await apiPost('/api/predict', {
      model_id: currentModel.id,
      inputs,
    });
    hideLoading();
    showPredResult(r, inputs);
    addToHistory(r.prediction, currentModel.name);
    showToast('Predicción realizada ✅', 'success');
  } catch(e) {
    hideLoading();
    showToast('Error: ' + e.message, 'error');
  }
}

function showPredResult(r, inputs) {
  document.getElementById('predFormSection').style.display = 'none';
  document.getElementById('predResultSection').style.display = 'block';

  document.getElementById('predClass').textContent = r.prediction;

  // Best probability
  const bestProb = Math.max(...Object.values(r.probabilities));
  document.getElementById('predConfidence').textContent =
    `Confianza: ${(bestProb * 100).toFixed(2)}%`;

  // Input summary
  const summaryHtml = Object.entries(inputs).map(([k,v]) =>
    `<div style="display:flex;justify-content:space-between;padding:.2rem 0;border-bottom:1px solid var(--border)">
       <span>${k}</span><strong>${v}</strong>
     </div>`).join('');
  document.getElementById('predInputSummary').innerHTML = summaryHtml;

  renderProbChart(r.probabilities, r.prediction);
  document.getElementById('predResultSection').scrollIntoView({ behavior:'smooth' });
}

function renderProbChart(probs, predicted) {
  const ctx = document.getElementById('probChart').getContext('2d');
  if (probChartInst) probChartInst.destroy();

  const labels = Object.keys(probs);
  const values = Object.values(probs).map(v => parseFloat((v * 100).toFixed(2)));
  const colors = labels.map(l =>
    l == predicted ? 'rgba(26,115,232,.85)' : 'rgba(100,116,139,.45)'
  );

  probChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Probabilidad (%)',
        data: values,
        backgroundColor: colors,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.raw.toFixed(2)}%` }
        },
        annotation: {}
      },
      scales: {
        x: {
          ticks: { color:'var(--text-secondary)', font:{weight:'600'} },
          grid:  { color:'var(--border)' }
        },
        y: {
          min: 0, max: 100,
          ticks: { color:'var(--text-muted)', callback: v => v + '%' },
          grid:  { color:'var(--border)' }
        }
      },
      animation: { duration:900, easing:'easeOutQuart' }
    }
  });
}

function fillRandom() {
  document.querySelectorAll('.pred-input').forEach(inp => {
    const isCat = inp.getAttribute('data-type') === 'categorical';
    if (isCat) {
        inp.value = "Ejemplo";
    } else {
        const min  = parseFloat(inp.min)  || 0;
        const max  = parseFloat(inp.max)  || 10;
        const val  = (Math.random() * (max - min) + min).toFixed(2);
        inp.value  = val;
    }
    inp.style.borderColor = '';
  });
  showToast('Valores aleatorios generados', 'info');
}

function clearForm() {
  document.querySelectorAll('.pred-input').forEach(inp => {
    inp.value = inp.placeholder;
    inp.style.borderColor = '';
  });
}

function resetPrediction() {
  document.getElementById('predResultSection').style.display = 'none';
  document.getElementById('predFormSection').style.display  = 'block';
}

function addToHistory(prediction, modelName) {
  predHistory.unshift({ prediction, model: modelName, time: new Date().toLocaleTimeString() });
  if (predHistory.length > 8) predHistory.pop();
  const el = document.getElementById('predHistory');
  el.innerHTML = predHistory.map(p => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:.35rem 0;border-bottom:1px solid var(--border)">
      <span style="font-weight:700;color:var(--blue-tech)">${p.prediction}</span>
      <small style="color:var(--text-muted)">${p.time}</small>
    </div>`).join('');
}
