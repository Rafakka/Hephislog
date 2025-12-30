from hephis_core.events.bus import event_bus
from hephis_core.swarm.decisions import get_decision, reset_decisions
from hephis_core.bootstrap import bootstrap_agents

def setup_function():
    event_bus.reset()
    reset_decisions()
    bootstrap_agents()

def test_clear_music_input_produces_result():
    run_id = "music-clear-1"

    print("EXACT:", event_bus.exact_handlers)
    print("WILDCARD:", event_bus.wildcard_handlers)

    event_bus.emit(
        "system.smells.post.extraction",
        {
            "run_id":run_id,
            "source":"music",
            "raw":{
                "domain":"music",
                "lyrics":["taking away..."],
                "chords":["C","G","Am","F"],
                "text":"taking away...",
            },
            "smells":{
                "music":0.9,
                "text":0.1,
            }
        }   
    )

    decision = get_decision(run_id)

    assert run_id is not None, "DecisionAgent received no run_id"
    assert decision is not None
    assert isinstance(decision, dict)
    assert decision.get("domain") == "music"
