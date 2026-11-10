import sqlite3
from pathlib import Path

from app.config import settings


SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"
LATEST_VERSION = 1


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def initialize_database() -> None:
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(schema_sql)
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            (LATEST_VERSION,),
        )
        conn.executemany(
            "INSERT OR IGNORE INTO roles (id, name) VALUES (?, ?)",
            [(1, "Administrator"), (2, "AssessmentManager"), (3, "Candidate")],
        )