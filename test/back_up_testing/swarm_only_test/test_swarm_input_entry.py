from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event
import hephis_core.agents.gatekeeper_agent
import hephis_core.agents.identifier_agent
import hephis_core.agents.decision_agent

def setup_function():
    event_bus.reset()

def test_system_input_events_enters_swarm():
    seen = []

    def spy(payload):
        seen.append(payload)
    
    event_bus.subscribe("system.input_received", spy)
    
    event_bus.emit (
        "system.input_received",
        {
            "input":"hello world",
            "run_id":"test-input-1",
            "source":"test",
        }
    )

    assert len(seen) == 1
    assert seen[0]["run_id"] == "test-input-1"