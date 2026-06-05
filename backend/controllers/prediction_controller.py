import os, json
import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify, send_file
from models.database import get_connection
import joblib

prediction_bp = Blueprint('prediction', __name__)

def load_model(training_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trainings WHERE id=?", (training_id,))
    tr = c.fetchone()
    conn.close()
    if not tr or not tr['model_path']:
        return None, None
    bundle = joblib.load(tr['model_path'])
    return bundle, tr

@prediction_bp.route('/manual/<int:training_id>', methods=['POST'])
def manual_predict(training_id):
    bundle, tr = load_model(training_id)
    if not bundle:
        return jsonify({'error': 'Modelo no encontrado'}), 404
    model = bundle['model']
    feature_names = bundle['feature_names']
    preprocessor = bundle.get('preprocessor')
    input_dict = {}
    for feat in feature_names:
        val = request.form.get(feat)
        if val is None:
            return jsonify({'error': f'Falta {feat}'}), 400
        try:
            input_dict[feat] = float(val) if val.replace('.','',1).replace('-','',1).isdigit() else val
        except:
            input_dict[feat] = val
    input_df = pd.DataFrame([input_dict])
    if preprocessor:
        input_processed = preprocessor.transform(input_df)
    else:
        input_processed = input_df.values
    proba = model.predict_proba(input_processed)[0]
    pred_class = model.classes_[np.argmax(proba)]
    confidence = round(np.max(proba)*100, 1)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO predictions (training_id, input_data, predicted_class, probability, confidence_level) VALUES (?,?,?,?,?)",
              (training_id, json.dumps(input_dict), str(pred_class), confidence/100.0, f"{confidence}%"))
    conn.commit()
    conn.close()
    return jsonify({
        'prediction': str(pred_class),
        'probability': confidence,
        'input': input_dict,
        'all_probabilities': {str(cls): round(p,4) for cls, p in zip(model.classes_, proba)}
    })

@prediction_bp.route('/csv/<int:training_id>', methods=['POST'])
def csv_predict(training_id):
    bundle, tr = load_model(training_id)
    if not bundle:
        return jsonify({'error': 'Modelo no encontrado'}), 404
    if 'file' not in request.files:
        return jsonify({'error': 'Archivo no enviado'}), 400
    file = request.files['file']
    try:
        df = pd.read_csv(file)
    except:
        return jsonify({'error': 'Error al leer CSV'}), 400
    model = bundle['model']
    feature_names = bundle['feature_names']
    preprocessor = bundle.get('preprocessor')
    if not all(feat in df.columns for feat in feature_names):
        missing = [feat for feat in feature_names if feat not in df.columns]
        return jsonify({'error': f'Faltan columnas: {", ".join(missing)}'}), 400
    X = df[feature_names]
    if preprocessor:
        X_processed = preprocessor.transform(X)
    else:
        X_processed = X.values
    probas = model.predict_proba(X_processed)
    preds = model.classes_[np.argmax(probas, axis=1)]
    confidences = np.max(probas, axis=1)*100
    results = df.copy()
    results['Prediccion'] = preds
    results['Confianza (%)'] = confidences.round(1)
    out_path = os.path.join('uploads', 'predictions_result.csv')
    results.to_csv(out_path, index=False)
    conn = get_connection()
    c = conn.cursor()
    for i in range(len(results)):
        input_json = json.dumps(X.iloc[i].to_dict())
        c.execute("INSERT INTO predictions (training_id, input_data, predicted_class, probability, confidence_level) VALUES (?,?,?,?,?)",
                  (training_id, input_json, str(preds[i]), confidences[i]/100.0, f"{confidences[i]:.1f}%"))
    conn.commit()
    conn.close()
    return send_file(out_path, as_attachment=True, download_name='predictions.csv')