
from .registry import event_bus

def on_event(event_name: str):
    """
    Decorator that automatically registers the function
    as a handler for the given event.
    """

    def decorator(func):
        event_bus.subscribe(event_name, func)
        return func

    return decorator
