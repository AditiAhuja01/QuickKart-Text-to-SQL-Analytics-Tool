import sqlite3
import os

# SQLite database file — stored right in the backend folder
DB_PATH = os.path.join(os.path.dirname(__file__), "quickkart.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # returns dict-like rows
    return conn

def run_query(sql: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        columns = list(results[0].keys()) if results else []
        return {
            "columns": columns,
            "rows": results,
            "count": len(results)
        }
    finally:
        conn.close()

def save_query_history(question: str, sql: str, result_count: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO query_history (question, sql_query, result_count, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (question, sql, result_count))
        conn.commit()
    finally:
        conn.close()

def get_history(limit: int = 20):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, question, sql_query, result_count, created_at
            FROM query_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def create_history_table():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                question     TEXT NOT NULL,
                sql_query    TEXT NOT NULL,
                result_count INTEGER DEFAULT 0,
                created_at   TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()
