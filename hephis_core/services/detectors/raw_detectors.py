
import json
from urllib.parse import urlparse
from pathlib import Path

def is_str(value) -> bool:
    return isinstance(value, str)

def is_url(value: str) -> bool:

    if not is_str(value):
        return False

    text = value.strip()

    result = urlparse(text)

    return all([result.scheme in ("http", "https"), result.netloc])

def is_html(value):

    if not is_str(value):
        return False

    text = value.strip()
    lower = text.lower()

    if lower.endswith((".html",".htm")):
        return True
    
    if "<" not in text and ">" not in text:
        return False
    
    common_tags = ["<html", "<div","<p","<span","<body","<head",
    "<script","<section","<article"]

    for tag in common_tags:
        if tag in text.lower():
            return True

    return False

def is_file(value):

    if not is_str(value):
        return False

    path = value.strip()

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

def is_text(value):

    if not isinstance(value, str):
        return False

    if is_url(value): return False
    if is_html(value): return False
    if is_json(value): return False
    if is_file(value): return False

    return True

def detect_raw_type(value, env):

    smells = env.smells

    if smells.get("html", 0) > 0.8 and is_html(value):
        return "html"

    if smells.get("json", 0) > 0.8 and is_json(value):
        return "json"

    if is_url(value):
        return "url"

    if is_html(value):
        return "html"

    if is_json(value):
        return "json"

    if is_file(value):
        return "file"

    if is_text(value):
        return "text"

    return "unknown"