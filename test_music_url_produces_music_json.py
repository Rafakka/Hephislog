import json
from pathlib import Path

from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.decision_store import decision_store
from hephis_core.infra.observability.report_store import reset_report
from hephis_core.bootstrap import bootstrap_agents

def test_music_url_produces_music_json(tmp_path):

    print("\n===EMIT INPUT EVENT ===")

    event_bus.reset()
    decision_store.reset()
    reset_report()
    run_context.reset()
    bootstrap_agents()

    run_id = "music-clear-1"
    
    print("\n===EMIT INPUT EVENT===")

    run_id = "test-music-url-1"

    payload = {
        "run_id": run_id,
        "source":"url",
        "input":"http://bettyloumusic.com/takeonme.htm",
        "domain_hint":"music",
    }

    event_bus.emit("system.input_received", payload)

    decison = decision_store.get(run_id)
    
    assert decison is not None, "No decision was stored"
    assert decison["domain"] == "music"

    output_dir = Path("data/output") / run_id
    assert output_dir.exists()

    json_files =list(output_dir.glob("*.json"))
    assert json_files

    with json_files[0].open() as f:
        data = json.load(f)
    
    assert data["domain"] == "music"
    assert "title" in data
    assert "chords" in data or "lyrics" in data
    assert "source_url" in data