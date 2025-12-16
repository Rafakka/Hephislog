
class Interpreter:
    domain: str = None

    def interpret(self, detected: dict, env):
        """
        Turn detector output into canonical internal data.
        Must return dict or None.
        """
        raise NotImplementedError