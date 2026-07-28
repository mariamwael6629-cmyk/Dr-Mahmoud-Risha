"""--- NEW FEATURE: lightweight schema-evolution helper (no Alembic in this project) ---
Adds newly-introduced columns to already-existing SQLite tables in place, so
upgrading the app does not require deleting clinic.db. Idempotent - skips any
column that is already present. Existing columns/tables are never touched.
"""
from sqlalchemy import text

from database import db

NEW_COLUMNS = {
    "appointments": [
        ("status", "VARCHAR(20) DEFAULT 'waiting'"),
        ("visit_type", "VARCHAR(30)"),
        ("visit_notes", "TEXT"),
        ("time", "VARCHAR(10)"),
    ],
    "medication_records": [
        ("generic_name", "VARCHAR(150)"),
        ("category", "VARCHAR(100)"),
        ("dosage", "VARCHAR(100)"),
    ],
    "patients": [
        ("medical_history_extra", "TEXT"),
    ],
}


def run_migrations():
    conn = db.engine.connect()
    try:
        for table, columns in NEW_COLUMNS.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
            for col_name, col_ddl in columns:
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_ddl}"))
        conn.commit()
    finally:
        conn.close()
