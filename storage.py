import sqlite3
from models import Finding

DB_PATH = "snack-scout.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            source_url TEXT,
            date_found DATE,
            why_it_matches_you TEXT,
            feedback TEXT DEFAULT NULL,
            UNIQUE(name, source_url)
        )
    """)
    conn.commit()
    return conn

def save_findings(conn, findings: list[Finding]) -> int:
    new_count = 0
    for f in findings:
        try:
            conn.execute(
                "INSERT INTO findings (name, category, source_url, date_found, why_it_matches_you) VALUES (?, ?, ?, ?, ?)", 
                (f.name, f.category, f.source_url, f.date_found.isoformat(), f.why_it_matches_you)
            )
            new_count += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    return new_count