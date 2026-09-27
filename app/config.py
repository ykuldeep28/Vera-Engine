import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "vera.db"))
LLM_PHRASING_ENABLED = os.getenv("LLM_PHRASING_ENABLED", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# App metadata for GET /v1/metadata
TEAM_NAME = "Team Vera Engine"
TEAM_MEMBERS = ["Vera AI"]
MODEL_NAME = "rule-engine-v1.2-deterministic"
APPROACH = "4-context deterministic rule engine with Jinja2 composition and SQLite WAL persistence"
CONTACT_EMAIL = "vera@example.com"
VERSION = "1.2.0"
SUBMITTED_AT = "2026-04-26T08:00:00Z"
