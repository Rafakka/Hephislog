
import re
import unicodedata
import os
from services.cleaners.data_cleaner import slugify

def save_json(json_data, domain, title, base_path=None):

    if base_path is None:
        base_path = Path("data")

    slug = slugify(title)

    dir_path = base_path / domain / slug
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / f"{domain}_{slug}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    return file_path