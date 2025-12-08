
class MusicImporter(BaseImporter):
    def fetch(self, url):
        from hephis_core.infra.sources.music_scraper import extract_chords_and_lyrics

        raw = extract_chords_and_lyrics(url)
        raw["url"] = url

        return raw

    def organize(self,raw):
        from hephis_core.services.cleaners.chord_cleaner import music_organizer
        sections = music_organizer(raw["paragraphs"])
        return {
            "sections": sections,
            "title": raw["title"],
            "url": raw["url"]
        }
    
    def normalize(self, organized):
        from hephis_core.modules.music_normalizer.normalizer import music_normalizer
        return music_normalizer(
            organized["sections"],
            url=organized["url"],
            run_id="django-api"
        )
    
    def map_to_model(self,normalized):
        return normalized