import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER,
            target_column TEXT,
            test_size REAL,
            accuracy REAL,
            precision REAL,
            recall REAL,
            f1_score REAL,
            auc REAL,
            trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            model_path TEXT,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        );
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_id INTEGER,
            input_data TEXT,
            predicted_class TEXT,
            probability REAL,
            confidence_level TEXT,
            predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (training_id) REFERENCES trainings(id)
        );
    ''')
    conn.commit()
    conn.close()
