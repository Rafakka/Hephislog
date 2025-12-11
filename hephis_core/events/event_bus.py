
class EventBus:
    def __init__(self):
        self.exact_handlers = {}       
        self.wildcard_handlers = {}

    @staticmethod
    def matches(pattern, event):
        """
        Returns True if event name matches a wildcard pattern.
        """
        if "*" not in pattern:
            return pattern == event

        before, after = pattern.split("*", 1)
        return event.startswith(before) and event.endswith(after)

    def subscribe(self, event_name: str, handler):
        """
        Registers a handler for exact or wildcard events.
        """
        if not callable(handler):
            raise TypeError("Handler must be callable")

        if "*" in event_name:
            self.wildcard_handlers.setdefault(event_name, []).append(handler)
        else:
            self.exact_handlers.setdefault(event_name, []).append(handler)

    def emit(self, event_name: str, payload):
        """
        Emits an event to all matching handlers.
        """
        for fn in self.exact_handlers.get(event_name, []):
            fn(payload)

        for pattern, handlers in self.wildcard_handlers.items():
            if self.matches(pattern, event_name):
                for fn in handlers:
                    fn(payload)
