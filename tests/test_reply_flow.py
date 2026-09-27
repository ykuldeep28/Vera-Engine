import pytest
from app.db import init_db
from app.reply.reply_engine import ReplyEngine

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_vera.db")
    monkeypatch.setattr("app.config.DB_PATH", test_db)
    monkeypatch.setattr("app.db.DB_PATH", test_db)
    init_db()

def test_auto_reply_hell():
    conv_id = "test_conv_auto"
    m_id = "m_001_drmeera"
    auto_msg = "Thank you for contacting us! Our team will respond shortly."

    # Turn 1: Reply with note
    r1 = ReplyEngine.handle_reply(conv_id, auto_msg, m_id, turn_number=1)
    assert r1["action"] == "send"
    assert "auto-reply" in r1["body"].lower()

    # Turn 2: Wait 4 hours
    r2 = ReplyEngine.handle_reply(conv_id, auto_msg, m_id, turn_number=2)
    assert r2["action"] == "wait"
    assert r2["wait_seconds"] == 14400

    # Turn 3: End conversation
    r3 = ReplyEngine.handle_reply(conv_id, auto_msg, m_id, turn_number=3)
    assert r3["action"] == "end"

def test_hostile_stop():
    conv_id = "test_conv_hostile"
    m_id = "m_001_drmeera"
    hostile_msg = "Stop messaging me. This is useless spam."

    r = ReplyEngine.handle_reply(conv_id, hostile_msg, m_id, turn_number=2)
    assert r["action"] == "end"
