from hephis_core.events.bus import event_bus

def on_event(event_name:str):
    def decorator(func):
        func.__event_name__ = event_name
        return func
    return decorator