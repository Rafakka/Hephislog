import json
from pathlib import Path

from hephis_core.events.bus import event_bus
from hephis_core.swarm.run_context import run_context
from hephis_core.swarm.decision_store import decision_store
from hephis_core.infra.observability.report_store import reset_report
from hephis_core.bootstrap import bootstrap_agents

def test_music_url_produces_recipe_json(tmp_path):

    print("\n===CHECKING BOOTSTRAP ===")

    event_bus.reset()
    decision_store.reset()
    reset_report()
    run_context.reset()
    bootstrap_agents()
    
    run_id = "test-recipe-url-1"

    payload = {
        "run_id": run_id,
        "source":"url",
        "input":"https://www.tudogostoso.com.br/receita/113143-massa-de-panqueca-simples.html",
        "domain_hint":"recipe",
    }

    print("\n===EMIT INPUT EVENT===")

    event_bus.emit("system.input_received", payload)

    decison = decision_store.get(run_id)
    assert decison is not None, "No decision was stored"
    assert decision["domain"] == "recipe"
    
    output_dir = Path("data/recipes") / run_id
    assert output_dir.exists(), "Recipe output directory was no created"

    json_files = list(base_dir.rglob("*.json"))
    assert json_files, "No recipe JSON files produced"

    with json_files[0].open() as f:
        data = json.load(f)

    assert "title" in data

    assert "ingredients" in data
    assert isinstance (data["ingredients"],list)

    assert "steps" in data
    assert isinstance (data["steps"],list)

    assert "url" in data
