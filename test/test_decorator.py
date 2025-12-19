from hephis_core.events.decorators import on_event
from hephis_core.events.event_bus import event_bus

def setup_function():
    event_bus.reset()

def test_on_event_decorator_registers_handler():
    recieved = []

    def handler(payload):
        recieved.append(payload)

        decorated = on_event("test.decorated")(handler)

        event_bus.emit("test.decorated",{"ok":True})

        assert recieved == [{"ok":True}]
        assert decorated is handler
    