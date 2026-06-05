from flask import Flask
from flask_cors import CORS
from controllers.dataset_controller import dataset_bp
from controllers.training_controller import training_bp
from controllers.prediction_controller import prediction_bp
from models.database import init_db
import os

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATASET_FOLDER'] = 'datasets'
app.config['MODEL_FOLDER'] = 'trained_models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

for folder in ['uploads', 'datasets', 'trained_models', 'static/plots']:
    os.makedirs(folder, exist_ok=True)

init_db()

app.register_blueprint(dataset_bp, url_prefix='/api/datasets')
app.register_blueprint(training_bp, url_prefix='/api/training')
app.register_blueprint(prediction_bp, url_prefix='/api/prediction')

@app.route('/api/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
