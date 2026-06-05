import os
import json
import sqlite3
from datetime import datetime

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from database.db import init_db, get_db
from services.train_service import train_model
from services.eval_service import evaluate_model
from services.predict_service import predict

# ── App setup ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
DS_DIR     = os.path.join(BASE_DIR, "datasets")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR,  exist_ok=True)
os.makedirs(DS_DIR,     exist_ok=True)

app = Flask(__name__)
CORS(app, origins="*")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024   # 50 MB


@app.before_request
def setup():
    init_db()


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ── Datasets ────────────────────────────────────────────────────────────────
BUILTIN = {
    "iris":          os.path.join(DS_DIR, "iris.csv"),
    "breast_cancer": os.path.join(DS_DIR, "breast_cancer.csv"),
}


@app.get("/api/datasets")
def list_datasets():
    builtin = [{"name": k, "source": "builtin"} for k in BUILTIN]
    uploads = []
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith(".csv"):
            uploads.append({"name": f[:-4], "source": "upload", "filename": f})
    return jsonify({"datasets": builtin + uploads})


@app.post("/api/upload")
def upload_dataset():
    if "file" not in request.files:
        return jsonify({"error": "No se encontró ningún archivo"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Solo se permiten archivos CSV"}), 400
    safe_name = os.path.basename(file.filename)
    path = os.path.join(UPLOAD_DIR, safe_name)
    file.save(path)
    return jsonify({"message": "Subido exitosamente", "filename": safe_name}), 201


def _load_dataset(name: str) -> pd.DataFrame:
    if name in BUILTIN:
        return pd.read_csv(BUILTIN[name])
    path = os.path.join(UPLOAD_DIR, name + ".csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset '{name}' no encontrado")
    return pd.read_csv(path)


@app.get("/api/dataset/<name>/info")
def dataset_info(name):
    try:
        df = _load_dataset(name)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    stats = {
        "rows":    int(df.shape[0]),
        "cols":    int(df.shape[1]),
        "columns": df.columns.tolist(),
        "dtypes":  {c: str(df[c].dtype) for c in df.columns},
        "nulls":   df.isnull().sum().to_dict(),
        "preview": df.head(10).fillna("").to_dict(orient="records"),
        "numeric_stats": json.loads(df.describe().fillna("").to_json()),
    }
    return jsonify(stats)


# ── Training ─────────────────────────────────────────────────────────────────
@app.post("/api/train")
def train():
    body = request.get_json()
    dataset_name  = body.get("dataset")
    features      = body.get("features", [])
    target        = body.get("target")
    test_size     = float(body.get("test_size", 0.3))
    max_iter      = int(body.get("max_iter", 1000))
    model_name    = body.get("model_name", f"model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")

    if not dataset_name or not features or not target:
        return jsonify({"error": "dataset, features, y target son obligatorios"}), 400

    try:
        df = _load_dataset(dataset_name)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    try:
        result = train_model(
            df=df,
            features=features,
            target=target,
            test_size=test_size,
            max_iter=max_iter,
            model_name=model_name,
            model_dir=MODEL_DIR,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Persist to DB
    db = get_db()
    db.execute(
        """INSERT INTO trained_models
           (name, dataset, features, target, accuracy, file_path, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            model_name,
            dataset_name,
            json.dumps(features),
            target,
            result["train_accuracy"],
            result["model_path"],
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()

    return jsonify(result), 201


# ── Models list ───────────────────────────────────────────────────────────────
@app.get("/api/models")
def list_models():
    db = get_db()
    rows = db.execute(
        "SELECT id, name, dataset, features, target, accuracy, created_at FROM trained_models ORDER BY id DESC"
    ).fetchall()
    models = []
    for r in rows:
        models.append({
            "id":         r["id"],
            "name":       r["name"],
            "dataset":    r["dataset"],
            "features":   json.loads(r["features"]),
            "target":     r["target"],
            "accuracy":   r["accuracy"],
            "created_at": r["created_at"],
        })
    return jsonify({"models": models})


# ── Evaluation ────────────────────────────────────────────────────────────────
@app.post("/api/evaluate")
def evaluate():
    body         = request.get_json()
    model_id     = body.get("model_id")
    dataset_name = body.get("dataset")

    if not model_id:
        return jsonify({"error": "model_id es obligatorio"}), 400

    db  = get_db()
    row = db.execute(
        "SELECT * FROM trained_models WHERE id = ?", (model_id,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Modelo no encontrado"}), 404

    features = json.loads(row["features"])
    target   = row["target"]
    ds_name  = dataset_name or row["dataset"]

    try:
        df = _load_dataset(ds_name)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    try:
        metrics = evaluate_model(
            model_path=row["file_path"],
            df=df,
            features=features,
            target=target,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(metrics)


# ── Prediction ────────────────────────────────────────────────────────────────
@app.post("/api/predict")
def make_prediction():
    body     = request.get_json()
    model_id = body.get("model_id")
    inputs   = body.get("inputs", {})

    if not model_id:
        return jsonify({"error": "model_id es obligatorio"}), 400

    db  = get_db()
    row = db.execute(
        "SELECT * FROM trained_models WHERE id = ?", (model_id,)
    ).fetchone()
    if not row:
        return jsonify({"error": "Modelo no encontrado"}), 404

    features = json.loads(row["features"])

    try:
        result = predict(
            model_path=row["file_path"],
            features=features,
            inputs=inputs,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Log prediction
    db.execute(
        """INSERT INTO predictions
           (model_id, input_data, prediction, probability, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (
            model_id,
            json.dumps(inputs),
            result["prediction"],
            json.dumps(result["probabilities"]),
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()

    return jsonify(result)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
