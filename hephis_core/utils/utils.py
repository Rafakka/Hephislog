from dataclasses import dataclass

@dataclass
class FakeFact:
    def __init__(self, stage, component, result):
        self.stage = stage
        self.component = component
        self.result = result