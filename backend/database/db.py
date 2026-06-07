import sqlite3
import os
from flask import g

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "app.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS trained_models (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            dataset     TEXT    NOT NULL,
            features    TEXT    NOT NULL,
            target      TEXT    NOT NULL,
            accuracy    REAL,
            file_path   TEXT,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id    INTEGER NOT NULL,
            input_data  TEXT,
            prediction  TEXT,
            probability TEXT,
            created_at  TEXT,
            FOREIGN KEY (model_id) REFERENCES trained_models(id)
        );
        """
    )
    db.commit()
