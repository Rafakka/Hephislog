import json
from pathlib import Path

from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.decision_store import decision_store
from hephis_core.infra.observability.report_store import reset_report, get_report
from hephis_core.bootstrap import bootstrap_agents

def test_music_url_produces_music_json(tmp_path):

    print("\n===EMIT INPUT EVENT ===")

    event_bus.reset()
    decision_store.reset()
    reset_report()
    run_context.reset()
    bootstrap_agents()
    
    print("\n===EMIT INPUT EVENT===")

    run_id = "test-music-url-1"

    payload = {
        "run_id": run_id,
        "source":"url",
        "input":"http://bettyloumusic.com/takeonme.htm",
        "domain_hint":"music",
    }

    event_bus.emit("system.input_received", payload)

    report = get_report(run_id)
    assert report["veredict"] == "Flow Completed"

    base_dir = Path("data/recipe")
    assert base_dir.exists()

    json_files = list(base_dir.rglob("*.json"))
    assert json_files, "No recipe json files produced"

    with json_files[0].open(encoding="utf-8") as f:
        data = json.load(f)

    assert "name" in data
    assert isinstance(data["name"],str)

    assert "steps" in data
    assert isinstance(data["steps"], str)

    assert "ingredients" in data
    assert isinstance(data["ingredients"], list)

    assert "source" in data