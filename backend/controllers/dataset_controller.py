import os, json
import pandas as pd
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models.database import get_connection

dataset_bp = Blueprint('dataset', __name__)
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route('/', methods=['GET'])
def list_datasets():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, uploaded_at FROM datasets ORDER BY uploaded_at DESC")
    rows = c.fetchall()
    conn.close()
    datasets = [dict(row) for row in rows]
    return jsonify(datasets)

@dataset_bp.route('/upload', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió archivo'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre vacío'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Solo se permiten CSV'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join('datasets', filename)
    file.save(save_path)
    try:
        df = pd.read_csv(save_path)
        if df.shape[0] < 10 or df.shape[1] < 2:
            os.remove(save_path)
            return jsonify({'error': 'Dataset debe tener al menos 10 filas y 2 columnas'}), 400
    except Exception as e:
        os.remove(save_path)
        return jsonify({'error': f'Error al leer CSV: {str(e)}'}), 400
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO datasets (name, path) VALUES (?,?)", (filename, save_path))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Dataset subido correctamente'}), 201

@dataset_bp.route('/<int:dataset_id>', methods=['GET'])
def view_dataset(dataset_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    df = pd.read_csv(row['path'])
    preview = df.head(10).to_dict(orient='records')
    columns = df.columns.tolist()
    dtypes = df.dtypes.astype(str).tolist()
    return jsonify({
        'id': row['id'],
        'name': row['name'],
        'shape': df.shape,
        'columns': columns,
        'dtypes': dtypes,
        'preview': preview
    })

@dataset_bp.route('/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404
    try:
        os.remove(row['path'])
    except:
        pass
    c.execute("DELETE FROM datasets WHERE id=?", (dataset_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Eliminado'})
