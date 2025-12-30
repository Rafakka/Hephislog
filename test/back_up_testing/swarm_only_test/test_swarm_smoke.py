from hephis_core.events.event_bus import event_bus
from hephis_core.events.decorators import on_event

def setup_function():
    event_bus.reset()

def test_event_bus_can_emit_and_receive():    
    received = []

    def handler(payload):
        received.append(payload)
    
    event_bus.subscribe("test.ping", handler)
    event_bus.emit("test.ping",{"ok":True})

    assert received == [{"ok":True}]