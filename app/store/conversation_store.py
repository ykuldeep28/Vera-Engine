from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.db import get_db_connection

class ConversationStore:
    @staticmethod
    def create_or_update_conversation(
        conversation_id: str,
        merchant_id: str,
        customer_id: Optional[str] = None,
        suppression_key: Optional[str] = None,
        state: str = "proposed",
        last_action_type: Optional[str] = None,
        auto_reply_count: Optional[int] = None
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT conversation_id, auto_reply_count FROM conversations WHERE conversation_id = ?", (conversation_id,))
                row = cursor.fetchone()
                if row:
                    new_auto_count = auto_reply_count if auto_reply_count is not None else row["auto_reply_count"]
                    cursor.execute(
                        """
                        UPDATE conversations SET
                            state = ?,
                            last_action_type = COALESCE(?, last_action_type),
                            auto_reply_count = ?,
                            updated_at = ?
                        WHERE conversation_id = ?
                        """,
                        (state, last_action_type, new_auto_count, now_iso, conversation_id)
                    )
                else:
                    new_auto_count = auto_reply_count if auto_reply_count is not None else 0
                    cursor.execute(
                        """
                        INSERT INTO conversations (
                            conversation_id, merchant_id, customer_id, suppression_key,
                            state, last_action_type, auto_reply_count, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (conversation_id, merchant_id, customer_id, suppression_key, state, last_action_type, new_auto_count, now_iso, now_iso)
                    )
        finally:
            conn.close()

    @staticmethod
    def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def add_message(conversation_id: str, direction: str, text: str, intent: Optional[str] = None):
        now_iso = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO messages (conversation_id, direction, text, intent, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (conversation_id, direction, text, intent, now_iso)
                )
        finally:
            conn.close()

    @staticmethod
    def get_messages(conversation_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC",
                (conversation_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
