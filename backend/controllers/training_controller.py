import os, time, json
import pandas as pd
from flask import Blueprint, request, jsonify
from models.database import get_connection
from services.ml_service import train_logistic_regression, evaluate_model, get_roc_data, get_confusion_matrix
from services.explainer import generate_explanation
import joblib

training_bp = Blueprint('training', __name__)

@training_bp.route('/columns/<int:dataset_id>')
def dataset_columns(dataset_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT path FROM datasets WHERE id=?", (dataset_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify([])
    df = pd.read_csv(row['path'])
    return jsonify(df.columns.tolist())

@training_bp.route('/start', methods=['POST'])
def start_training():
    dataset_id = int(request.form['dataset_id'])
    target = request.form['target_column']
    test_size = float(request.form['test_size']) / 100.0
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,))
    ds = c.fetchone()
    conn.close()
    if not ds:
        return jsonify({'error': 'Dataset no encontrado'}), 404
    df = pd.read_csv(ds['path'])
    if target not in df.columns:
        return jsonify({'error': 'Columna objetivo invalida'}), 400
    start = time.time()
    model, X_test, y_test, feature_names, preprocessor = train_logistic_regression(df, target, test_size)
    elapsed = round(time.time() - start, 3)
    metrics = evaluate_model(model, X_test, y_test)
    roc = get_roc_data(model, X_test, y_test)
    cm = get_confusion_matrix(model, X_test, y_test)
    model_filename = f"model_{dataset_id}_{int(time.time())}.joblib"
    model_path = os.path.join('trained_models', model_filename)
    joblib.dump({'model': model, 'feature_names': feature_names, 'preprocessor': preprocessor}, model_path)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO trainings (dataset_id, target_column, test_size, accuracy, precision, recall, f1_score, auc, model_path)
                 VALUES (?,?,?,?,?,?,?,?,?)''',
              (dataset_id, target, test_size, metrics['accuracy'], metrics['precision'],
               metrics['recall'], metrics['f1'], metrics['auc'], model_path))
    training_id = c.lastrowid
    conn.commit()
    conn.close()
    coefs = dict(zip(feature_names, model.coef_[0]))
    explanation = generate_explanation(metrics['accuracy'], coefs)
    return jsonify({
        'training_id': training_id,
        'metrics': metrics,
        'roc_data': roc,
        'confusion_matrix': cm,
        'feature_names': feature_names,
        'coefficients': {k: round(v,4) for k,v in coefs.items()},
        'explanation': explanation,
        'elapsed': elapsed,
        'n_samples': df.shape[0],
        'n_features': len(feature_names)
    })

@training_bp.route('/list', methods=['GET'])
def list_trainings():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, dataset_id, target_column, accuracy, precision, recall, f1_score, auc, trained_at FROM trainings ORDER BY trained_at DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@training_bp.route('/<int:training_id>', methods=['GET'])
def training_detail(training_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trainings WHERE id=?", (training_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    # Si existe el modelo guardado, obtener feature_names
    result = dict(row)
    if row['model_path'] and os.path.exists(row['model_path']):
        bundle = joblib.load(row['model_path'])
        result['feature_names'] = bundle.get('feature_names', [])
    else:
        result['feature_names'] = []
    return jsonify(result)