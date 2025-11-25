
import re
import unicodedata
from services.cleaners import slugify

def save_json(json_text, domain, title):

    filename = slugify(title) + ".json"

    folder = os.path.join("data", "ingested", domain)
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(json_text)

    return path
