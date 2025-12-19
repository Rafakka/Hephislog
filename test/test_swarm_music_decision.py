from hephis_core.events.event_bus import event_bus
from hephis_core.swarm.decisions import get_decision, reset_decisions
import hephis_core.agents.decision_agent

def setup_function():
    event_bus.reset()

def test_clear_music_input_produces_result():
    run_id = "music-clear-1"

    event_bus.emit(
        "system.input_received",
        {
            "input":"C G Am F",
            "run_id":run_id,
            "source":"test",
        }   
    )

    decision = get_decision(run_id)

    assert run_id is not None, "DecisionAgent received no run_id"
    assert decision is not None
    assert isinstance(decision, dict)
    assert decision.get("domain") == "music"
