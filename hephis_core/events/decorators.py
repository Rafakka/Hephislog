from hephis_core.events.event_bus import EventBus

def on_event(event_name:str):

    def decorator(func):
        event_bus.subscribe(event_name, func)

        return func
        
    return decorator