/* evaluate.js */
let confusionChartInst = null;
let rocChartInst = null;
let modelsCache = [];

document.addEventListener('DOMContentLoaded', loadModels);

async function loadModels() {
  try {
    const data = await apiGet('/api/models');
    modelsCache = data.models;
    const sel = document.getElementById('modelSelect');
    if (!data.models.length) {
      sel.innerHTML = '<option value="">-- Sin modelos entrenados --</option>';
      return;
    }
    sel.innerHTML = '<option value="">-- Seleccionar modelo --</option>' +
      data.models.map(m =>
        `<option value="${m.id}">${m.name} (${m.dataset} · Acc: ${(m.accuracy*100).toFixed(1)}%)</option>`
      ).join('');
    sel.addEventListener('change', () => showModelMeta(sel.value));
  } catch(e) {
    document.getElementById('modelSelect').innerHTML =
      '<option value="">-- Backend no disponible --</option>';
  }
}

function showModelMeta(id) {
  const m = modelsCache.find(x => x.id == id);
  if (!m) { document.getElementById('modelMeta').style.display='none'; return; }
  document.getElementById('modelMeta').style.display = 'block';
  document.getElementById('modelMetaBadges').innerHTML = `
    <span class="badge-custom badge-blue"><i class="bi bi-database"></i> ${m.dataset}</span>
    <span class="badge-custom badge-green"><i class="bi bi-tag"></i> Target: ${m.target}</span>
    <span class="badge-custom badge-purple"><i class="bi bi-list-columns"></i> Features: ${m.features.length}</span>
    <span class="badge-custom badge-orange"><i class="bi bi-calendar"></i> ${m.created_at ? m.created_at.split('T')[0] : '—'}</span>
  `;
  // Pre-fill eval dataset
  const dsSel = document.getElementById('evalDsSelect');
  if (['iris','breast_cancer'].includes(m.dataset)) dsSel.value = m.dataset;
}

async function runEvaluation() {
  const modelId = document.getElementById('modelSelect').value;
  if (!modelId) { showToast('Selecciona un modelo', 'error'); return; }

  const ds = document.getElementById('evalDsSelect').value || undefined;

  showLoading('Evaluando modelo...');
  try {
    const r = await apiPost('/api/evaluate', { model_id: parseInt(modelId), dataset: ds });
    hideLoading();

    document.getElementById('evalPlaceholder').style.display = 'none';
    document.getElementById('evalResults').style.display     = 'block';

    // Metric cards
    document.getElementById('mAccuracy').textContent  = pct(r.accuracy);
    document.getElementById('mPrecision').textContent = pct(r.precision);
    document.getElementById('mRecall').textContent    = pct(r.recall);
    document.getElementById('mF1').textContent        = pct(r.f1_score);

    renderConfusionMatrix(r.confusion_matrix, r.classes);
    renderROC(r.roc, r.classes);
    renderClassReport(r.classification_report, r.classes);

    document.getElementById('evalResults').scrollIntoView({ behavior:'smooth' });
    showToast('Evaluación completada ✅', 'success');
  } catch(e) {
    hideLoading();
    showToast('Error: ' + e.message, 'error');
  }
}

function renderConfusionMatrix(cm, classes) {
  const ctx = document.getElementById('confusionChart').getContext('2d');
  if (confusionChartInst) confusionChartInst.destroy();

  // Flatten for bubble/bar representation — use grouped bar
  const datasets = classes.map((cls, i) => ({
    label: 'Real: ' + cls,
    data:  cm[i],
    backgroundColor: cm[i].map((_, j) =>
      i === j ? 'rgba(26,115,232,.8)' : 'rgba(239,68,68,.65)'
    ),
    borderRadius: 5,
  }));

  confusionChartInst = new Chart(ctx, {
    type: 'bar',
    data: { labels: classes.map(c => 'Pred: ' + c), datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { labels: { color:'var(--text-secondary)', font:{size:11} } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label} → ${ctx.label}: ${ctx.raw}`
          }
        }
      },
      scales: {
        x: { ticks:{color:'var(--text-muted)'}, grid:{color:'var(--border)'} },
        y: { ticks:{color:'var(--text-muted)'}, grid:{color:'var(--border)'}, beginAtZero:true }
      }
    }
  });
}

function renderROC(roc, classes) {
  const ctx = document.getElementById('rocChart').getContext('2d');
  if (rocChartInst) rocChartInst.destroy();

  const COLORS = ['#1a73e8','#10b981','#f59e0b','#8b5cf6','#ef4444'];
  const datasets = [];
  let bestAuc = 0;

  Object.entries(roc).forEach(([key, val], i) => {
    datasets.push({
      label: `${key === 'binary' ? 'ROC' : key} (AUC=${val.auc.toFixed(3)})`,
      data: val.fpr.map((f, j) => ({ x: f, y: val.tpr[j] })),
      borderColor: COLORS[i % COLORS.length],
      borderWidth: 2.5,
      pointRadius: 0,
      tension: 0.3,
      fill: i === 0 ? { target:'origin', above: 'rgba(26,115,232,.08)' } : false,
    });
    if (val.auc > bestAuc) bestAuc = val.auc;
  });

  // Diagonal reference
  datasets.push({
    label: 'Aleatorio (AUC=0.5)',
    data: [{x:0,y:0},{x:1,y:1}],
    borderColor: 'rgba(239,68,68,.45)',
    borderWidth: 1.5,
    borderDash: [5,5],
    pointRadius: 0,
  });

  document.getElementById('aucBadge').textContent = 'AUC: ' + bestAuc.toFixed(3);

  rocChartInst = new Chart(ctx, {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      showLine: true,
      plugins: {
        legend: { labels:{ color:'var(--text-secondary)', font:{size:11} } }
      },
      scales: {
        x: { min:0,max:1, title:{display:true,text:'FPR (1 - Specificity)',color:'var(--text-muted)'},
             ticks:{color:'var(--text-muted)'}, grid:{color:'var(--border)'} },
        y: { min:0,max:1, title:{display:true,text:'TPR (Recall/Sensitivity)',color:'var(--text-muted)'},
             ticks:{color:'var(--text-muted)'}, grid:{color:'var(--border)'} }
      }
    }
  });
}

function renderClassReport(report, classes) {
  const rows = classes.map(cls => {
    const d = report[String(cls)] || {};
    return {
      Clase:     cls,
      Precision: d.precision != null ? pct(d.precision) : '—',
      Recall:    d.recall    != null ? pct(d.recall)    : '—',
      'F1-Score':d['f1-score']!= null ? pct(d['f1-score']) : '—',
      Soporte:   d.support != null ? d.support : '—',
    };
  });
  // Weighted avg
  const wa = report['weighted avg'] || {};
  rows.push({
    Clase: '⚖️ Weighted Avg',
    Precision: wa.precision != null ? pct(wa.precision) : '—',
    Recall:    wa.recall    != null ? pct(wa.recall)    : '—',
    'F1-Score':wa['f1-score']!= null ? pct(wa['f1-score']) : '—',
    Soporte:   wa.support != null ? wa.support : '—',
  });
  buildTable(document.getElementById('classReport'), rows);
}
