import pytest
from bs4 import BeautifulSoup
from services.cleaners.chord_cleaner import music_organizer


MESSY_PARAGRAPHS = [
    "<p><span class='taggedChord' data-original-chord='Am'>Am</span> "
    "<span class='taggedChord' data-original-chord='D'></span></p>",

    "<p>Talking away,</p>",

    "<p style='color:red'> &nbsp; <span class='taggedChord' data-original-chord='Am'>Am</span> "
    "<span class='taggedChord' data-original-chord='D'>D</span> G  C Bm (3x)</p>",

    "<p>I'll say it anyway,</p>",

    "<p>This line has no chord in it.</p>",
    "<p>Just text, no chords here.</p>",

    "<p><span class='taggedChord' data-original-chord='C'>C</span> Em</p>",
    "<p><span class='taggedChord' data-original-chord='F'>F</span> G Am</p>",
    "<p>I'm alive</p>",

    "<p><span class='taggedChord' data-original-chord='G/B'>G/B</span> "
    "F# <span class='taggedChord' data-original-chord='C#m'>C#m</span></p>",

    "<p>Take on me</p>"
]


EXPECTED_OUTPUT = [
    {"chords": ["Am", "D"], "lyrics": "Talking away,"},
    {"chords": ["Am", "D", "G", "C", "Bm"], "lyrics": "I'll say it anyway,"},
    {"chords": ["C", "Em", "F", "G", "Am"], "lyrics": "I'm alive"},
    {"chords": ["G/B", "F#", "C#m"], "lyrics": "Take on me"},
]


def make_tag(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.p


def test_music_organizer_messy():
    tags = [make_tag(txt) for txt in MESSY_PARAGRAPHS]
    result = music_organizer(tags)
    assert result == EXPECTED_OUTPUT
