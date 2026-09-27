import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from app.db import get_db_connection

class ContextStore:
    @staticmethod
    def upsert_context(scope_type: str, scope_id: str, version: int, data: Dict[str, Any]) -> Tuple[bool, int]:
        """
        Upsert versioned context.
        Returns: (success: bool, current_version: int)
        If incoming version <= existing version, returns (False, existing_version).
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT version FROM context_versions WHERE scope_type = ? AND scope_id = ?",
                (scope_type, scope_id)
            )
            row = cursor.fetchone()
            if row:
                existing_version = row["version"]
                if version <= existing_version:
                    return False, existing_version

            now_iso = datetime.now(timezone.utc).isoformat()
            data_json = json.dumps(data, ensure_ascii=False)
            cursor.execute(
                """
                INSERT INTO context_versions (scope_type, scope_id, version, data, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(scope_type, scope_id) DO UPDATE SET
                    version = excluded.version,
                    data = excluded.data,
                    updated_at = excluded.updated_at
                """,
                (scope_type, scope_id, version, data_json, now_iso)
            )
            conn.commit()
            return True, version
        finally:
            conn.close()

    @staticmethod
    def get_context(scope_type: str, scope_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM context_versions WHERE scope_type = ? AND scope_id = ?",
                (scope_type, scope_id)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row["data"])
            return None
        finally:
            conn.close()

    @staticmethod
    def get_context_counts() -> Dict[str, int]:
        conn = get_db_connection()
        counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT scope_type, COUNT(*) as cnt FROM context_versions GROUP BY scope_type"
            )
            for row in cursor.fetchall():
                scope = row["scope_type"]
                if scope in counts:
                    counts[scope] = row["cnt"]
            return counts
        finally:
            conn.close()
