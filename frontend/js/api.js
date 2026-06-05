const API_BASE = 'https://tu-backend.onrender.com/api';  // Reemplazar con URL real

const api = {
    async getDatasets() {
        const res = await fetch(`${API_BASE}/datasets/`);
        return res.json();
    },
    async uploadDataset(formData) {
        const res = await fetch(`${API_BASE}/datasets/upload`, { method: 'POST', body: formData });
        return res.json();
    },
    async deleteDataset(id) {
        const res = await fetch(`${API_BASE}/datasets/${id}`, { method: 'DELETE' });
        return res.json();
    },
    async getDatasetColumns(id) {
        const res = await fetch(`${API_BASE}/training/columns/${id}`);
        return res.json();
    },
    async trainModel(formData) {
        const res = await fetch(`${API_BASE}/training/start`, { method: 'POST', body: formData });
        return res.json();
    },
    async getTrainings() {
        const res = await fetch(`${API_BASE}/training/list`);
        return res.json();
    },
    async predictManual(trainingId, formData) {
        const res = await fetch(`${API_BASE}/prediction/manual/${trainingId}`, { method: 'POST', body: formData });
        return res.json();
    },
    async predictCsv(trainingId, formData) {
        const res = await fetch(`${API_BASE}/prediction/csv/${trainingId}`, { method: 'POST', body: formData });
        return res.blob();
    }
};
