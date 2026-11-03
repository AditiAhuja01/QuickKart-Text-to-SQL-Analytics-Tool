import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.path.join(os.path.dirname(__file__), "quickkart.db")

_USE_SQLITE = None

def is_postgres_available():
    """Check if PostgreSQL is accessible once, cache the decision."""
    global _USE_SQLITE
    if _USE_SQLITE is not None:
        return not _USE_SQLITE

    host = os.getenv("DB_HOST", "localhost")
    if os.getenv("USE_LOCAL_DB", "").lower() in ("true", "1") or not host or "supabase" in host:
        print("[QuickKart DB] Using local quickkart.db SQLite engine.")
        _USE_SQLITE = True
        return False

    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host,
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "quickkart"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            connect_timeout=2
        )
        conn.close()
        _USE_SQLITE = False
        print("[QuickKart DB] Connected to PostgreSQL successfully.")
        return True
    except Exception:
        print("[QuickKart DB] PostgreSQL unavailable. Using local quickkart.db SQLite engine.")
        _USE_SQLITE = True
        return False

def get_connection():
    """Return database connection and engine type ('postgres' or 'sqlite')."""
    if is_postgres_available():
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "quickkart"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )
        return conn, "postgres"
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def get_readonly_connection():
    """Return a strictly read-only database connection with a query timeout."""
    if is_postgres_available():
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "quickkart"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            connect_timeout=3
        )
        conn.set_session(readonly=True)
        return conn, "postgres"
    else:
        # SQLite read-only URI mode: physically blocks write/mutation operations
        db_uri = f"file:{os.path.abspath(DB_FILE)}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True, timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def run_query(sql: str):
    """Executes validated SELECT queries against the read-only database engine."""
    # Enforce safe row limit: cap at 500 rows if no LIMIT specified
    cleaned_sql = sql.strip().rstrip(";")
    if "LIMIT" not in cleaned_sql.upper():
        cleaned_sql += " LIMIT 500"

    conn, db_type = get_readonly_connection()
    try:
        if db_type == "postgres":
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(cleaned_sql)
                results = [dict(row) for row in cursor.fetchall()] if cursor.description else []
        else:
            cursor = conn.cursor()
            cursor.execute(cleaned_sql)
            results = [dict(row) for row in cursor.fetchall()] if cursor.description else []

        columns = list(results[0].keys()) if results else []
        return {
            "columns": columns,
            "rows": results,
            "count": len(results),
            "executed_sql": cleaned_sql
        }
    finally:
        conn.close()

def save_query_history(question: str, sql: str, result_count: int):
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgres":
            cursor.execute("""
                INSERT INTO query_history (question, sql_query, result_count, created_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            """, (question, sql, result_count))
        else:
            cursor.execute("""
                INSERT INTO query_history (question, sql_query, result_count, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (question, sql, result_count))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_history(limit: int = 20):
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgres":
            from psycopg2.extras import RealDictCursor
            with conn.cursor(cursor_factory=RealDictCursor) as p_cursor:
                p_cursor.execute("""
                    SELECT id, question, sql_query, result_count, created_at
                    FROM query_history
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in p_cursor.fetchall()]
        else:
            cursor.execute("""
                SELECT id, question, sql_query, result_count, created_at
                FROM query_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def create_history_table():
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgres":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id           SERIAL PRIMARY KEY,
                    question     TEXT NOT NULL,
                    sql_query    TEXT NOT NULL,
                    result_count INTEGER DEFAULT 0,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    question     TEXT NOT NULL,
                    sql_query    TEXT NOT NULL,
                    result_count INTEGER DEFAULT 0,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


