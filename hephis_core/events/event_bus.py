
class EventBus:
    def __init__(self):
        self.handlers = {} 

    def subscribe(self, event_name: str, handler):
        """
        Registers a handler for an event.
        """
        if not callable(handler):
            raise TypeError("Handler must be callable")

        if event_name not in self._handlers:
            self._handlers[event_name] = []

        # Prevent duplicates (optional, but useful)
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def emit(self, event_name: str, payload=None):
        """
        Emits an event and triggers all handlers subscribed to it.
        """

        handlers = self._handlers.get(event_name, [])

        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                print(f"[EventBus] Handler error on '{event_name}': {e}")
        