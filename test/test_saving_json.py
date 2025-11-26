import json
import pytest
from utils.json_handler import save_json
from services.cleaners.data_cleaner import slugify

@pytest.mark.parametrize(
    "input_dict, domain, title",
    [
        (
            {
                "title": "Take On Me",
                "instrument": "guitar",
                "key": "Am",
                "sections": [
                    {
                        "name": "Verse",
                        "lines": [
                            {"chords": ["Am", "D"], "lyrics": "Talking away,"}
                        ]
                    }
                ],
                "source": "bettylou",
                "url": "http://example.com",
                "run_id": "12345"
            },
            "music",
            "Take On Me"
        ),
        (
            {
                "title": "Simple Recipe",
                "ingredients": ["salt", "water"],
                "steps": ["mix", "boil"]
            },
            "recipes",
            "Simple Recipe"
        )
    ]
)

def test_save_json(tmp_path, input_dict, domain, title):

    file_path = save_json(
        json_data=input_dict,
        domain=domain,
        title=title,
        base_path=tmp_path
    )

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved == input_dict

    slug = slugify(title)
    assert slug in file_path.name

    assert file_path.parent == tmp_path / domain / slug
