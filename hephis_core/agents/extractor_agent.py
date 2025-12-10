from hephis_core.events.decorators import on_event
from hephis_core.events.registry import event_bus as announcer
from hephis_core.services.detectors.raw_detectors import is_url
from hephis_core.infra.sources.t_g_scraper import fetch_and_extract, extract_tg_recipe
from hephis_core.infra.sources.music_scraper import extract_chords_and_lyrics, extract_chords_from_html


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

    def extract_from_html(self, html):
        try:
            raw_recipe = extract_tg_recipe(html)
            if self.is_valid_recipe(raw_recipe):
                return("recipe", raw_recipe)
        except:
            pass

        try:
            raw_music = extract_chords_from_html(html)
            if self.is_valid_music(raw_music):
                return("music",raw_music)
        except:
            pass


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
    
    @on_event("system.html_received")
    def handle_html(self, payload):

        html = payload["html"]
        domain, raw = self.extract_from_html(html)

        announcer.announce(
            domain=domain,
            action="raw_extracted",
            data={
                "url": None,
                "raw": raw
            }
        )