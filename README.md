# 🧠 LinReg AI — Predicción con Regresión Lineal

> **Proyecto Final — Curso de Inteligencia Artificial y Machine Learning 2026**  
> Plataforma web académica completa para entrenar, evaluar y desplegar modelos de predicción basados en Regresión Lineal.

---

## 🚀 Demo

| Componente | URL |
|------------|-----|
| Frontend (Vercel) | `https://tu-proyecto.vercel.app` |
| Backend API (Render) | `https://tu-api.onrender.com` |

---

## 📋 Características

- ✅ **Landing page** estilo SaaS con teoría completa sobre Regresión Lineal
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
git clone https://github.com/tu-usuario/linreg-ai.git
cd "linreg-ai/Proyecto final"
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
- Predicción de especies de flores: *setosa*, *versicolor*, *virginica*
- Features: `sepal_length`, `sepal_width`, `petal_length`, `petal_width`

### 🔬 Breast Cancer Dataset
- **Filas**: 569 | **Features**: 30 | **Clases**: 2
- Predicción de tumores: maligno (0) / benigno (1)
- Features: 30 características celulares numéricas

---

## 🔬 Pipeline de Machine Learning (Soporte Universal v2)

La arquitectura ha sido diseñada para aceptar cualquier dataset sin importar su complejidad. La limpieza, imputación y codificación ocurren en tiempo de ejecución:

```
CSV / Dataset (Texto, Números, Nulos)
      ↓
Limpieza de Datos Pandas (Auto-parseo decimal, NaNs)
      ↓
Detección Automática de Target (Discretización para regresión continua)
      ↓
Train / Test Split (scikit-learn)
      ↓
ColumnTransformer (Manejo de Features Mixtos)
  ├── 🔢 Numéricos → SimpleImputer(mean) → StandardScaler
  └── 🔠 Categóricos (Texto) → SimpleImputer(mode) → OneHotEncoder
      ↓
LogisticRegression (Clasificador, max_iter configurable)
      ↓
Evaluación (Accuracy, Precision, Recall, F1, ROC)
      ↓
Serialización (joblib → .joblib) con versión de preprocesamiento
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








Documentación Técnica Detallada — LinReg AI
Esta documentación proporciona una visión técnica profunda y exhaustiva de todos los componentes, flujos de datos y decisiones arquitectónicas de LinReg AI, una plataforma de Machine Learning construida para entrenar y evaluar modelos de clasificación usando Regresión Logística.

1. Arquitectura del Sistema
El sistema utiliza una arquitectura Cliente-Servidor (Frontend / Backend) comunicada puramente a través de una API RESTful.

Frontend (Cliente): Aplicación Single Page Application (SPA) construida con HTML puro, CSS vanilla y JavaScript (ES2022). No utiliza frameworks como React o Angular, manteniendo un peso ligero. La reactividad y enrutamiento visual se manejan manipulando el DOM (Document Object Model) directamente.
Backend (Servidor): Aplicación escrita en Python 3.10+ usando el microframework Flask. Actúa como motor de Machine Learning utilizando la librería scikit-learn y como interfaz de persistencia de datos mediante SQLite3.
1.1 Diagrama de Arquitectura
Mermaid diagram
2. Modelado de Base de Datos (SQLite)
El sistema utiliza una base de datos relacional ligera (database.db) que se autogenera al iniciar la aplicación. Cuenta con dos tablas principales:

Tabla: trained_models
Almacena el historial y los metadatos de los modelos entrenados.

id (INTEGER PRIMARY KEY): Identificador único del modelo.
name (TEXT): Nombre asignado por el usuario (ej. modelo_20260606...).
dataset (TEXT): Nombre del archivo o dataset utilizado (ej. iris).
features (TEXT): Array en formato JSON con las características usadas.
target (TEXT): La variable dependiente u objetivo.
accuracy (REAL): La precisión obtenida en el conjunto de entrenamiento.
file_path (TEXT): Ruta absoluta en el disco hacia el archivo binario .joblib.
created_at (TEXT): Fecha y hora en formato ISO 8601.
Tabla: predictions
Audita las predicciones realizadas por los usuarios usando modelos existentes.

id (INTEGER PRIMARY KEY)
model_id (INTEGER): Llave foránea lógica hacia trained_models.
input_data (TEXT): JSON con el diccionario de variables introducidas por el usuario.
prediction (TEXT): La clase final predicha por el modelo.
probability (TEXT): JSON con el desglose de probabilidades para cada clase posible.
created_at (TEXT): Fecha y hora de la predicción.
3. Flujo de Machine Learning (Soporte Universal V2)
El pipeline de ML ha sido diseñado para aceptar Cualquier Estructura de Dataset. Esto se logra mediante un preprocesamiento condicional y transformadores avanzados en scikit-learn.

3.1 Tratamiento de la Variable Objetivo (target)
El modelo utilizado es LogisticRegression, que es estrictamente un algoritmo de Clasificación.

Eliminación de Nulos: Se eliminan todas las filas del dataset donde la variable objetivo es NaN.
Detección de Continuidad: Utilizando sklearn.utils.multiclass.type_of_target, se verifica si la variable es continuous (ej. precios, edad decimal).
Discretización Automática: Si es continua, el backend la transforma en 3 categorías (Low, Medium, High) utilizando pandas.qcut (cuantiles) o pandas.cut (intervalos fijos) si falla por exceso de valores idénticos.
Label Encoding: Si el objetivo es de tipo texto, se usa LabelEncoder para transformarlo en enteros (0, 1, 2...) y poder ser consumido por el algoritmo.
3.2 Pipeline de Variables Independientes (features)
Se aplica un ColumnTransformer que bifurca el procesamiento dependiendo del tipo de dato subyacente. Antes de esto, se intenta limpiar numéricamente los campos de texto reemplazando comas , por puntos ..

Ruta Numérica (int64, float64):
Paso 1: SimpleImputer(strategy='mean') → Rellena valores vacíos con el promedio numérico de la columna.
Paso 2: StandardScaler() → Escala los datos (Media=0, Desviación Estándar=1) para que los coeficientes de la Regresión Logística converjan rápidamente y sean comparables entre sí.
Ruta Categórica / Texto (object, category):
Paso 1: SimpleImputer(strategy='most_frequent') → Rellena nulos con la moda (el valor más repetido).
Paso 2: OneHotEncoder(handle_unknown='ignore') → Convierte cada categoría en una columna binaria independiente (ej. Color_Rojo: 1, Color_Azul: 0). Si durante la predicción aparece una categoría nunca antes vista, la ignora sin fallar.
3.3 Entrenamiento y Guardado
División: Se usa train_test_split para separar la data. Si las clases están desbalanceadas y la estratificación falla, se hace un fallback automático a una división sin estratificar.
Serialización: El ColumnTransformer, StandardScaler, OneHotEncoder, LogisticRegression y el LabelEncoder se empaquetan en un único diccionario de Python junto a la bandera preprocessing_version: 2. Todo esto se guarda en el disco duro usando joblib.dump().
4. API REST: Especificación de Endpoints
4.1 Subida y Exploración de Datos
GET /api/datasets: Retorna arreglos separados para datasets builtin (nativos) y uploads (archivos CSV subidos).
POST /api/upload: Recibe un multipart/form-data con el campo file. Valida que la extensión sea .csv y lo guarda en la carpeta /backend/uploads.
GET /api/dataset/<name>/info: Utiliza Pandas para calcular metadatos en tiempo real:
Conteo de filas y columnas.
Tipos de datos (dtypes).
Diccionario de valores nulos.
Estadísticas descriptivas (media, min, max) generadas por df.describe().
4.2 Entrenamiento
POST /api/train
Payload (JSON): dataset (string), features (array de strings), target (string), test_size (float), max_iter (int), model_name (string).
Proceso: Carga el CSV, construye y ejecuta el pipeline de Machine Learning (V2), calcula las precisiones en los conjuntos Train/Test, extrae los coeficientes de regresión usando get_feature_names_out() y guarda todo el bundle en disco y SQLite.
Respuesta: Información del modelo entrenado y arreglo de coeficientes.
4.3 Evaluación de Rendimiento
POST /api/evaluate
Payload (JSON): model_id (int).
Proceso: Reconstruye el dataset usado en el entrenamiento. Detecta la versión del modelo. Discretiza el target si es necesario y pasa los datos por la función de transformación del modelo. Calcula predicciones en lote (y_pred y y_proba).
Métricas Retornadas:
accuracy: Porcentaje total de aciertos.
precision, recall, f1_score: Métricas ponderadas para evaluar el desempeño equilibrado.
confusion_matrix: Matriz 2D relacionando Valores Verdaderos vs Valores Predichos.
classification_report: Diccionario con métricas detalladas por clase individual.
roc: Diccionario que contiene las tasas de Falsos Positivos (fpr), Verdaderos Positivos (tpr) y el Área Bajo la Curva (auc) para cada clase generada usando label_binarize.
4.4 Predicción (Inferencia)
POST /api/predict
Payload (JSON): model_id (int), inputs (Diccionario { feature_name: value }).
Proceso: Carga el modelo .joblib. Construye un DataFrame de 1 sola fila asegurando que el orden de las columnas coincida con el esperado. Si el modelo es versión 2, respeta los valores de texto introducidos y deja que el ColumnTransformer aplique el One-Hot Encoding. Ejecuta pipeline.predict() y pipeline.predict_proba().
Respuesta: { "prediction": "Clase", "probabilities": {"Clase A": 0.85, "Clase B": 0.15} }
5. Diseño y Arquitectura del Frontend (JavaScript)
El Frontend interactúa con esta API mediante la función envolvente apiGet() y apiPost() que controlan cabeceras JSON y capturan errores para mostrar notificaciones flotantes (Toasts).

5.1 Gestión de Estado Global
La aplicación mantiene variables de estado volátiles en cada script (currentModel, datasetStats, datasetDtypes) para evitar consultar constantemente la API cuando el usuario interactúa con la página actual.

5.2 Generación Dinámica de Interfaces (predict.js)
El formulario de predicción se construye en tiempo de ejecución (buildPredForm).

Obtiene los dtypes y numeric_stats del dataset origen.
Por cada feature:
Si el dtype es numérico, genera un <input type="number"> con validación de rangos min y max correspondientes a la realidad de los datos.
Si el dtype es object (texto categórico), genera un <input type="text"> para aceptar palabras.
Si el usuario selecciona "Rellenar con datos aleatorios", el sistema genera un número aleatorio dentro del rango detectado, o inserta la palabra "Ejemplo" en campos de texto para pruebas rápidas.
5.3 Renderizado de Gráficos (Chart.js)
Toda la visualización de datos delegó los cáculos matemáticos pesados al backend y utiliza Chart.js exclusivamente para la representación:

Evaluación: Genera una Matriz de Confusión renderizada sobre un <canvas> o usando divs con colores calculados matemáticamente respecto al valor máximo de la matriz para crear un efecto de "Mapa de Calor" (Heatmap). Renderiza curvas ROC superponiendo las distintas clases de manera dinámica.
Predicción: Renderiza un gráfico de barras mostrando la confianza (probabilidad) para cada una de las clases predichas.
6. Mantenimiento y Escalabilidad Futura
Soporte de Regresión Pura: Actualmente el sistema fuerza la Regresión Logística (clasificación). Para expandirlo a Regresión Lineal pura, se debe crear un bifurcador en train_service.py que importe LinearRegression de scikit-learn y enrute la lógica basado en una elección explícita del usuario desde la interfaz.
Base de datos: SQLite es adecuado para proyectos demostrativos o pequeños. Para escalarlo a producción con miles de usuarios concurrentes, la conexión database/db.py puede ser migrada a PostgreSQL usando SQLAlchemy.