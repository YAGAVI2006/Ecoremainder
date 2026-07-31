"""
EcoReminder Database Module
Provides connection pooling, row parsing, schema initialization, and data access methods.
"""

import os
import sqlite3
from datetime import datetime
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def parse_row(row):
    if not row:
        return None
    d = dict(row)
    if "created_at" in d and d["created_at"]:
        if isinstance(d["created_at"], str):
            try:
                clean_date = d["created_at"].split(".")[0].replace("T", " ")
                d["created_at"] = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
    return d


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def fetch_all_complaints():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, u.name AS user_name, co.name AS collector_name
        FROM complaints c
        LEFT JOIN users u ON c.user_id = u.id
        LEFT JOIN collectors co ON c.assigned_collector = co.id
        ORDER BY c.created_at DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [parse_row(r) for r in rows]


def fetch_complaint_counts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
    in_progress = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Collected'")
    collected = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total, pending, in_progress, collected
