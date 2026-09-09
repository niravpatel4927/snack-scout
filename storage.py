import sqlite3
import os
from dotenv import load_dotenv
import psycopg2
from models import Finding

load_dotenv()
DB_PATH = "snack-scout.db"

def init_db():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id SERIAL PRIMARY KEY,
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
    cur = conn.cursor()
    for f in findings:
        try:
            cur.execute(
                "INSERT INTO findings (name, category, source_url, date_found, why_it_matches_you) VALUES (%s, %s, %s, %s, %s)",
                (f.name, f.category, f.source_url, f.date_found, f.why_it_matches_you),
            )
            conn.commit()
            new_count += 1
        except psycopg2.errors.UniqueViolation:
            conn.rollback()  # Postgres requires a rollback after a failed statement before the connection can be reused

    return new_count