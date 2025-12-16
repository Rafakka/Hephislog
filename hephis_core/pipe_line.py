from hephis_core.environment import ENV
from hephis_core.agents.sniffer_agent import SnifferAgent
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.router import route

def process_input(raw_input):
    """
    Main cognitive pipeline entrypoint.
    Returns interpreted result or None.
    """

    # 1. Reset environment
    ENV.reset()

    # 2. Sniff
    sniffer = SnifferAgent()
    sniffer.sniff(raw_input)

    # 3. Detect raw type (shape)
    raw_type = detect_raw_type(raw_input, ENV)

    # 4. Prepare data based on raw type
    # (minimal for now – you already have extractors elsewhere)
    data = raw_input

    # 5. Route + detect + interpret
    result = route(data, ENV)

    return result
