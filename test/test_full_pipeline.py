import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup

from infra.sources.music_scraper import extract_chords_and_lyrics
from services.cleaners.chord_cleaner import music_organizer
from schemas.mappers.music_mapper import map_music_data
from services.packers.universal_packer import pack_data
from utils.json_handler import save_json


EXPECTED_TAKE_ON_ME = {
    "title": "Take On Me",
    "instrument": None,
    "key": None,
    "sections": [
        {
            "name": "main",
            "lines": [
                {"chords": ["Am","D"], "lyrics": "Talking away,"},
                {"chords": ["C","Em","F","G","Am"], "lyrics": "I'm alive"}
            ]
        }
    ],
    "source": "local_test",
    "url": "local://test",
    "run_id": "test_run_001"
}

def test_full_pipeline_music(tmp_path):

    html_file = Path("test/fixtures/take_on_me_sample.html")
    html_text = html_file.read_text(encoding="utf-8")

    soup = BeautifulSoup(html_text, "html.parser")
    extracted = extract_chords_and_lyrics(soup)

    organized = music_organizer(extracted)

    mapped = map_music_data(
        title="Take On Me",
        sections=organized,
        source="local_test",
        url="local://test",
        run_id="test_run_001",
        instrument=None,
        key=None
    )
    
    packed = pack_data("music", mapped)

    file_path = packed["path"]
    assert file_path.exists()

    loaded = json.loads(file_path.read_text("utf-8"))

    assert loaded["title"] == "Take On Me"
    assert loaded["sections"] == mapped.model_dump()["sections"]
    assert loaded["source"] == "local_test"
    assert loaded["url"] == "local://test"
    assert loaded["run_id"] == "test_run_001"
