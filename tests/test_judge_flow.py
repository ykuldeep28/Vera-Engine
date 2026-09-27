import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_vera.db")
    monkeypatch.setattr("app.config.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    init_db()

client = TestClient(app)

def test_full_judge_lifecycle():
    # 1. Healthz
    r = client.get("/v1/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "contexts_loaded" in r.json()

    # 2. Metadata
    r = client.get("/v1/metadata")
    assert r.status_code == 200
    assert r.json()["version"] == "1.2.0"

    # 3. Context Push (Category)
    r = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": {"slug": "dentists", "voice": {"tone": "peer_clinical"}}
    })
    assert r.status_code == 200
    assert r.json()["accepted"] is True

    # 4. Context Push Duplicate Version -> Expect 409 Conflict
    r = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": {"slug": "dentists"}
    })
    assert r.status_code == 409
    assert r.json()["accepted"] is False
    assert r.json()["reason"] == "stale_version"

    # 5. Push Merchant & Trigger
    client.post("/v1/context", json={
        "scope": "merchant",
        "context_id": "m_001_drmeera_dentist_delhi",
        "version": 1,
        "payload": {"merchant_id": "m_001_drmeera_dentist_delhi", "category_slug": "dentists", "identity": {"name": "Dr. Meera's Dental Clinic", "owner_first_name": "Meera"}}
    })
    client.post("/v1/context", json={
        "scope": "trigger",
        "context_id": "trg_001_research_digest_dentists",
        "version": 1,
        "payload": {"id": "trg_001_research_digest_dentists", "kind": "research_digest", "merchant_id": "m_001_drmeera_dentist_delhi", "urgency": 2}
    })

    # 6. Tick
    r = client.post("/v1/tick", json={
        "now": "2026-04-26T10:35:00Z",
        "available_triggers": ["trg_001_research_digest_dentists"]
    })
    assert r.status_code == 200
    actions = r.json()["actions"]
    assert len(actions) == 1
    action = actions[0]
    assert action["send_as"] == "vera"
    assert "JIDA" in action["body"] or "Dr. Meera" in action["body"]
    assert "http" not in action["body"]  # Guarantee no URLs!

    # 7. Reply (Engaged)
    r = client.post("/v1/reply", json={
        "conversation_id": action["conversation_id"],
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "message": "Yes please send the abstract.",
        "turn_number": 2
    })
    assert r.status_code == 200
    assert r.json()["action"] == "send"
