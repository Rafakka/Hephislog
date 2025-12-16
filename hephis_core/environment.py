from datetime import datetime

ENV = Environment()

class Environment:
    def __init__(self):
        self.reset()

    def reset(self):
        self.source = None
        self.mode = "prod"
        self.timestamp = datetime.utcnow()
        self.flags = set()
        self.metadata = {}
        self.smells = {}

    def set(self, key, value):
        setattr(self, key, value)

    def add_flag(self, flag: str):
        self.flags.add(flag)

    def add_smell(self, name: str, score: float):
        self.smells[name] = max(self.smells.get(name, 0), score)

    def snapshot(self) -> dict:
        return {
            "source": self.source,
            "mode": self.mode,
            "flags": list(self.flags),
            "metadata": self.metadata,
            "smells": self.smells,
        }