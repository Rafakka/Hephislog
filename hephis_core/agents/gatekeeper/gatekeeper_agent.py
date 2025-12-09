
from hephis_core.services.cleaners.data_cleaner import is_url

class GatekeeperAgent:

    def __init__(self, announcer):
        self.announcer = announcer

    def process(self, incoming):

        if is_url(incoming):

            self.announcer.announce(
                domain="system",
                action="url_received",
                data={"url": incoming}
            )
            return
    