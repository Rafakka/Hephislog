
from services.detectors.chord_detector import (is_root, is_accidental, is_quality, 
is_bass, is_main_chord, is_chord, extract_chords_from_tokens, looks_like_chord_line,)
import pytest

@pytest.mark.parametrize("token, expected", [
    ("A", True),
    ("Z", False),
    ("Bb", False),
])
def test_is_root(token, expected):
    assert is_root(token) == expected

@pytest.mark.parametrize("token, expected", [
    ("F#", True),
    ("Bb", True),
    ("Am", False),
    ("G", False)
])
def test_is_accidental(token, expected):
    assert is_accidental(token) == expected

@pytest.mark.parametrize("token, expected", [
    ("m", True),
    ("maj7", True),
    ("dim", True),
    ("sus4", True),
    ("haha", False)
])
def test_is_quality(token, expected):
    assert is_quality(token) == expected

@pytest.mark.parametrize("token, expected", [
    ("G", True),
    ("F#", True),
    ("Bb", True),
    ("G7", False),
    ("3",False)
])
def test_is_bass(token, expected):
    assert is_bass(token) == expected

@pytest.mark.parametrize("token, expected",[
    ("Am", True),
    ("Cmaj7", True),
    ("F#dim", True),
    ("G/B", False),
    ("Z#", False),
    ("A!", False)
])
def test_is_main_chord(token, expected):
    assert is_main_chord(token) == expected

@pytest.mark.parametrize("token, expected",[
    ("Am", True),
    ("F#m", True),
    ("G/B", True),
    ("C/Eb", True),
    ("sus4", False),
    ("hello", False)
])
def test_is_chord(token, expected):
    assert is_chord(token)== expected

@pytest.mark.parametrize("token, expected",[
    ("Am D G C Bm", True ),
    ("G/B F#m C", True ),
    ("Am D G C Bm", True ),
    ("Take on me", False),
    ("Hello world", False),
    ("Am D G", True)
])
def test_looks_like_chord(token, expected):
    assert looks_like_chord_line(token) == expected

@pytest.mark.parametrize("token, expected",[
    ("Am D G C", ["Am","D","G","C"]),
    ("Am - D - G",["Am","D","G"]),
    ("G/B F# C#m", ["G/B", "F#", "C#m"]),
    ("hello world", [])
])
def test_extract_chords_from_tokens(token, expected):
    assert extract_chords_from_tokens(token) == expected