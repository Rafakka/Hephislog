import json
from pathlib import Path
from hephis_core.services.cleaners.data_cleaner import slugify
from hephis_core.utils.logger_decorator import log_action

BASE_PROCESSED_DIR = Path("data")

def ensure_processed_folder(domain: str, title: str) -> Path:
    """
    Ensure the processed output folder exists.
    Example: data/recipes/bolo_de_cenoura/
    """
    slug = slugify(title)
    folder = BASE_PROCESSED_DIR / domain / slug
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def get_processed_folder(domain, title):
    slug = slugify(title)
    folder = BASE_PROCESSED_DIR /domain/slug
    return folder

@log_action(action="write processed json", meta_fields=["domain", "title"])
def write_processed_json(domain: str, title: str, json_dict: dict) -> Path:
    """
    Save final processed JSON.
    Filename convention: <domain>_<slug>.json
    """
    folder = ensure_processed_folder(domain, title)
    slug = slugify(title)
    filename = f"{domain}_{slug}.json"
    filepath = folder / filename

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(json_dict, f, indent=2, ensure_ascii=False)

    return filepath