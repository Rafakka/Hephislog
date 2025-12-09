from hephis_core.infra.sources.t_g_scraper import fetch_and_extract
from hephis_core.infra.sources.music_scraper import extract_chords_and_lyrics

class ExtractorAgent:

    def is_valid_recipe(self, raw):
        return (
            isinstance(raw, dict)
            and "ingredients" in raw
            and "steps" in raw
        )

    def is_valid_music(self, raw):
            return (
                isinstance(raw, dict)
                and "paragraphs" in raw
                and "title" in raw
            )

    def extract_url(self, url):
        try:
            raw_recipe = fetch_and_extract(url)
            if self.is_valid_recipe(raw_recipe):
                return ("recipe", raw_recipe)
        except:
            pass

        try:
            raw_music = extract_chords_and_lyrics(url)
            if self.is_valid_music(raw_music):
                return ("music", raw_music)
        except:
            pass

        return ("system", None)

    @on_event("system.url_received")
    def handle_url(self, payload):

        url = payload["url"]

        domain, raw = self.extract_url(url)

        announcer.announce(
            domain=domain,
            action="raw_extracted",
            data={
                "url": url,
                "raw": raw
            }
        )