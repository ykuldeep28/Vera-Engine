import sqlite3
import os
from pathlib import Path
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    db_file = Path(DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        # 1. Versioned Context Store
        conn.execute("""
        CREATE TABLE IF NOT EXISTS context_versions (
            scope_type   TEXT NOT NULL,
            scope_id     TEXT NOT NULL,
            version      INTEGER NOT NULL,
            data         TEXT NOT NULL,
            updated_at   TEXT NOT NULL,
            PRIMARY KEY (scope_type, scope_id)
        );
        """)

        # 2. Suppression & Send History Log
        conn.execute("""
        CREATE TABLE IF NOT EXISTS suppression_log (
            suppression_key TEXT PRIMARY KEY,
            merchant_id      TEXT NOT NULL,
            trigger_type     TEXT NOT NULL,
            last_sent_at     TEXT,
            decline_count    INTEGER DEFAULT 0,
            last_decline_at  TEXT,
            opted_out        INTEGER DEFAULT 0
        );
        """)

        # 3. Conversations State Machine
        conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id  TEXT PRIMARY KEY,
            merchant_id      TEXT NOT NULL,
            customer_id      TEXT,
            suppression_key  TEXT,
            state            TEXT NOT NULL,
            last_action_type TEXT,
            auto_reply_count INTEGER DEFAULT 0,
            created_at       TEXT,
            updated_at       TEXT
        );
        """)

        # 4. Append-Only Messages Log
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id  TEXT NOT NULL,
            direction        TEXT NOT NULL,
            text             TEXT NOT NULL,
            intent           TEXT,
            created_at       TEXT
        );
        """)
    conn.close()
