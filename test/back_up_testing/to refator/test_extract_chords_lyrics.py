from infra.sources.music_scraper import extract_chords_and_lyrics

html = "http://bettyloumusic.com/takeonme.htm"

results = extract_chords_and_lyrics(html)

print(results)
