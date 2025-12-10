
import json
from urllib.parse import urlparse
from pathlib import Path

def is_str(input) -> bool:
    if not isinstance(input, str):
        raise TypeError("Expected a string, got:" +str(type(input)))
        return input

def is_url(text: str) -> bool:

    if not is_str(input):
        return False

    text = input.strip()

    result = urlparse(text)

    return all([result.scheme in ("http", "https"), result.netloc])

def is_html(input):

    if not is_str(input):
        return False

    text = input.strip()

    if is_url(text):
        return False
    
    if "<" not in text and ">" not in text:
        return False
    
    common_tags = ["<html", "<div","<p","<span","<body","<head",
    "<script","<section","<article"]

    for tag in common_tags:
        if tag in text.lower():
            return True

    return True

def is_file(input):

    if not is_str(input):
        return False

    path = input.strip()

    if is_url(path):
        return False
    
    if is_html(path):
        return False

    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            return True
    except:
        return False

    return False

def is_json(value):
    if not isinstance(value, str):
        return False
    try:
        json.loads(value)
        return True
    except:
        return False

def is_text(input):

    if not isinstance(value, str):
        return False

    if is_url(value): return False
    if is_html(value): return False
    if is_json(value): return False
    if is_file(value): return False

    return True

def detect_raw_type(value):
    if is_url(value):
        return "url"
    if is_html(value):
        return "html"
    if is_file(value):
        return "file"
    if is_json(value):
        return "json"
    if is_text(value):
        return "text"

    return "unknown_input"