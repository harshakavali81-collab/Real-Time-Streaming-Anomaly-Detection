from src.demo import run_demo
from src.sinks.store import Store

def test_offline_end_to_end(tmp_path):
    db = "sqlite:///" + str(tmp_path / "demo.db")
    result = run_demo(events=240, db=db, seed=91)
    assert result["inserted"] == 240
    assert result["summary"]["events"] == 240
    assert result["summary"]["evaluation"]["labelled"] == 240
    assert result["summary"]["p95_processing_ms"] is not None
    assert any(r["anomaly"] for r in Store(db).list_events(limit=240))

def test_offline_seeded_replay_is_idempotent(tmp_path):
    db = "sqlite:///" + str(tmp_path / "same.db")
    assert run_demo(30, db, seed=3)["inserted"] == 30
    assert run_demo(30, db, seed=3)["inserted"] == 0
