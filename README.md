# 🧠 LogReg AI — Clasificación con Regresión Logística

> **Proyecto Final — Curso de Inteligencia Artificial y Machine Learning 2026**  
> Plataforma web académica completa para entrenar, evaluar y desplegar modelos de clasificación basados en Regresión Logística.

---

## 🚀 Demo

| Componente | URL |
|------------|-----|
| Frontend (Vercel) | `https://tu-proyecto.vercel.app` |
| Backend API (Render) | `https://tu-api.onrender.com` |

---

## 📋 Características

- ✅ **Landing page** estilo SaaS con teoría completa sobre Regresión Logística
- ✅ **Dashboard** con selector de datasets y carga de CSV personalizado
- ✅ **Módulo de entrenamiento** con selección de features, split configurable y coeficientes
- ✅ **Módulo de evaluación** con Accuracy, Precision, Recall, F1, Matriz de Confusión y Curva ROC
- ✅ **Módulo de predicción** con formulario dinámico y probabilidades por clase
- ✅ **Modo oscuro / claro** con persistencia en localStorage
- ✅ **Responsive** — funciona en móvil, tablet y escritorio
- ✅ **SQLite** para persistencia de modelos y predicciones
- ✅ Datasets integrados: **Iris** y **Breast Cancer**
- ✅ Soporte para **CSV personalizado**

---

## 🛠️ Tecnologías

### Backend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.10+ | Lenguaje base |
| Flask | 3.0.3 | Framework web |
| Scikit-Learn | 1.5.1 | Modelos ML |
| Pandas | 2.2.2 | Manipulación de datos |
| NumPy | 1.26.4 | Operaciones numéricas |
| Joblib | 1.4.2 | Serialización de modelos |
| SQLite | built-in | Base de datos |
| Gunicorn | 22.0.0 | Servidor WSGI (producción) |

### Frontend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| HTML5 | — | Estructura |
| CSS3 | — | Estilos personalizados |
| JavaScript | ES2022 | Lógica del cliente |
| Bootstrap | 5.3.3 | Componentes UI |
| Chart.js | 4.4.3 | Gráficos interactivos |
| Google Fonts (Inter) | — | Tipografía |

---

## 📁 Estructura del Proyecto

```
Proyecto final/
├── backend/
│   ├── app.py                   # Flask app principal
│   ├── requirements.txt         # Dependencias Python
│   ├── Procfile                 # Render deployment
│   ├── generate_datasets.py     # Genera CSVs de scikit-learn
│   ├── database/
│   │   └── db.py                # SQLite init & helpers
│   ├── services/
│   │   ├── train_service.py     # Lógica de entrenamiento
│   │   ├── eval_service.py      # Métricas de evaluación
│   │   └── predict_service.py   # Predicción
│   ├── datasets/
│   │   ├── iris.csv
│   │   └── breast_cancer.csv
│   ├── models/                  # Modelos .joblib guardados
│   └── uploads/                 # CSVs subidos por el usuario
└── frontend/
    ├── index.html               # Landing page
    ├── dashboard.html           # Panel de control
    ├── train.html               # Módulo entrenamiento
    ├── evaluate.html            # Módulo evaluación
    ├── predict.html             # Módulo predicción
    ├── css/
    │   └── styles.css           # Sistema de diseño completo
    └── js/
        ├── main.js              # Utilidades compartidas
        ├── dashboard.js
        ├── train.js
        ├── evaluate.js
        └── predict.js
```

---

## ⚙️ Instalación y Ejecución Local

### Requisitos previos
- Python 3.10 o superior
- pip

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/logreg-ai.git
cd "logreg-ai/Proyecto final"
```

### 2. Configurar el entorno virtual

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Generar los datasets integrados

```bash
python generate_datasets.py
```

Salida esperada:
```
✅  iris.csv  →  (150, 5)
✅  breast_cancer.csv  →  (569, 31)
Done.
```

### 5. Iniciar el backend Flask

```bash
python app.py
```

El servidor correrá en: `http://localhost:5000`

### 6. Abrir el frontend

Abre `frontend/index.html` directamente en tu navegador, o usa un servidor estático:

```bash
# Con Python
cd ../frontend
python -m http.server 8080
# Visita: http://localhost:8080
```

---

## 🌐 API REST — Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET`  | `/api/health` | Estado del servidor |
| `GET`  | `/api/datasets` | Lista de datasets disponibles |
| `POST` | `/api/upload` | Subir dataset CSV |
| `GET`  | `/api/dataset/<name>/info` | Info y preview del dataset |
| `POST` | `/api/train` | Entrenar modelo |
| `GET`  | `/api/models` | Lista de modelos guardados |
| `POST` | `/api/evaluate` | Evaluar modelo con métricas |
| `POST` | `/api/predict` | Predicción sobre nuevos datos |

### Ejemplo: Entrenar un modelo

```bash
curl -X POST http://localhost:5000/api/train \
  -H "Content-Type: application/json" \
  -d '{
    "dataset": "iris",
    "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
    "target": "species",
    "test_size": 0.3,
    "max_iter": 1000,
    "model_name": "iris_v1"
  }'
```

### Ejemplo: Hacer una predicción

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "inputs": {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    }
  }'
```

---

## ☁️ Despliegue en la Nube

### Backend → Render

1. Crea una cuenta en [render.com](https://render.com)
2. Nuevo servicio → **Web Service**
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python generate_datasets.py`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3
5. Deploy 🚀

### Frontend → Vercel

1. Crea una cuenta en [vercel.com](https://vercel.com)
2. Importa tu repositorio
3. Configura:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Other (Static)
4. **Antes de desplegar**, actualiza `API_BASE` en `frontend/js/main.js`:
   ```js
   const API_BASE = "https://tu-api.onrender.com";  // URL de Render
   ```
5. Deploy ▲

---

## 📊 Datasets Incluidos

### 🌸 Iris Dataset
- **Filas**: 150 | **Features**: 4 | **Clases**: 3
- Clasificación de especies de flores: *setosa*, *versicolor*, *virginica*
- Features: `sepal_length`, `sepal_width`, `petal_length`, `petal_width`

### 🔬 Breast Cancer Dataset
- **Filas**: 569 | **Features**: 30 | **Clases**: 2
- Clasificación de tumores: maligno (0) / benigno (1)
- Features: 30 características celulares numéricas

---

## 🔬 Pipeline de Machine Learning

```
CSV / Dataset
      ↓
Preprocesamiento (Pandas)
      ↓
Train / Test Split (scikit-learn)
      ↓
StandardScaler (normalización)
      ↓
LogisticRegression (max_iter configurable)
      ↓
Evaluación (Accuracy, Precision, Recall, F1, ROC)
      ↓
Serialización (joblib → .joblib)
      ↓
API REST (Flask)
      ↓
Predicción en tiempo real
```

---

## 🎨 Diseño

- **Tema**: Oscuro/Claro con toggle persistente
- **Paleta**: `#0d1b2a` (navy) · `#1a73e8` (tech blue) · `#00d4ff` (cyan)
- **Tipografía**: Inter (Google Fonts)
- **Animaciones**: Scroll reveal, hover effects, orbs flotantes
- **Gráficos**: Chart.js — Sigmoid, Scatter, Bar, ROC, Confusion Matrix

---

## 👥 Equipo

Proyecto Final — Curso de Inteligencia Artificial y Machine Learning 2026

---

## 📄 Licencia

MIT License — Libre para uso académico y educativo.
