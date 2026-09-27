import pytest
from app.db import init_db
from app.store.suppression_store import SuppressionStore
from app.domain.suppression_rules import SuppressionGate

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_vera.db")
    monkeypatch.setattr("app.config.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    init_db()

def test_suppression_cooldown_and_opt_out():
    key = "research:dentists:2026-W17"
    merchant_id = "m_001_drmeera"

    # Before send
    is_supp, reason = SuppressionGate.check_suppression(key, merchant_id)
    assert is_supp is False

    # Record send
    SuppressionStore.record_send(key, merchant_id, "research_digest")

    # After send -> Suppressed
    is_supp, reason = SuppressionGate.check_suppression(key, merchant_id)
    assert is_supp is True
    assert reason == "suppressed_recent_send"

    # Opt-out test
    opt_key = "opt_out_key"
    SuppressionStore.record_opt_out(opt_key, merchant_id)
    is_supp, reason = SuppressionGate.check_suppression(opt_key, merchant_id)
    assert is_supp is True
    assert reason == "hard_opt_out"
