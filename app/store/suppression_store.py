from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.db import get_db_connection

class SuppressionStore:
    @staticmethod
    def record_send(suppression_key: str, merchant_id: str, trigger_type: str, sent_at: Optional[str] = None):
        if not sent_at:
            sent_at = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO suppression_log (suppression_key, merchant_id, trigger_type, last_sent_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(suppression_key) DO UPDATE SET
                        last_sent_at = excluded.last_sent_at
                    """,
                    (suppression_key, merchant_id, trigger_type, sent_at)
                )
        finally:
            conn.close()

    @staticmethod
    def record_decline(suppression_key: str, merchant_id: str, trigger_type: str):
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO suppression_log (suppression_key, merchant_id, trigger_type, decline_count, last_decline_at)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(suppression_key) DO UPDATE SET
                        decline_count = decline_count + 1,
                        last_decline_at = excluded.last_decline_at
                    """,
                    (suppression_key, merchant_id, trigger_type, now_iso)
                )
        finally:
            conn.close()

    @staticmethod
    def record_opt_out(suppression_key: str, merchant_id: str, trigger_type: str = "opt_out"):
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO suppression_log (suppression_key, merchant_id, trigger_type, opted_out, last_decline_at)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(suppression_key) DO UPDATE SET
                        opted_out = 1,
                        last_decline_at = excluded.last_decline_at
                    """,
                    (suppression_key, merchant_id, trigger_type, now_iso)
                )
        finally:
            conn.close()

    @staticmethod
    def get_suppression_entry(suppression_key: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppression_log WHERE suppression_key = ?", (suppression_key,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
