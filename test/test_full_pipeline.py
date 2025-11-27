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

    file_path = save_json(
        json_data=packed,
        domain="music",
        title="Take On Me",
        base_path=tmp_path
    )

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved == packed
    assert saved == EXPECTED_TAKE_ON_ME

    assert file_path.parent == tmp_path / "music" / "take-on-me"
