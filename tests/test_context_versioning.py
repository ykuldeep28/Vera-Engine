import pytest
from app.db import init_db
from app.store.context_store import ContextStore

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_vera.db")
    monkeypatch.setattr("app.config.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    init_db()

def test_context_idempotency_and_versioning():
    # 1. First push v1
    success, ver = ContextStore.upsert_context("category", "dentists", 1, {"name": "Dentists"})
    assert success is True
    assert ver == 1

    # 2. Re-push v1 -> Should fail with stale_version
    success, ver = ContextStore.upsert_context("category", "dentists", 1, {"name": "Dentists"})
    assert success is False
    assert ver == 1

    # 3. Push v2 -> Should succeed and update
    success, ver = ContextStore.upsert_context("category", "dentists", 2, {"name": "Dentists Updated"})
    assert success is True
    assert ver == 2

    # 4. Fetch context -> should match v2
    data = ContextStore.get_context("category", "dentists")
    assert data["name"] == "Dentists Updated"
