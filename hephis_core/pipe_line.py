from hephis_core.environment import ENV
from hephis_core.agents.sniffer_agent import SnifferAgent
from hephis_core.services.detectors.raw_detectors import detect_raw_type
from hephis_core.router import route
import requests

def process_input(raw_input):
    """
    Main cognitive pipeline entrypoint.
    Returns interpreted result or None.
    """
    try:
        ENV.reset()
        sniffer = SnifferAgent()
        sniffer.sniff(raw_input)
        raw_type = detect_raw_type(raw_input, ENV)

        if raw_type == "url":
            response = requests.get(raw_input, timeout=10)
            data = response.text
        else:
            data = raw_input

        result = route(data, ENV)
        return result

    except Exception as e:
        print("PIPELINE ERROR:", type(e).__name__, str(e))
        raise