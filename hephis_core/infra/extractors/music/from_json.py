
def extract_music_from_json(obj:dict)-> dict | None:

    if not isinstance(obj, dict):
        return None

    if "paragraphs" in obj and "title" in obj:
        return {
            "title":obj["title"],
            "paragraphs":obj["paragraphs"],
            "source":"json_raw"
        }

    return None
