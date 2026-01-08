from pathlib import Path
import json
from hephis_core.services.cleaners.data_cleaner import slugify


def serialize_json(validated_object):
    json_dict = validated_object.model_dump()
    return json_dict

def resolve_output_path(title, domain, base_path):
    slug = slugify(title)
    dir = base_path / domain / slug
    file = dir / f"{domain}_{slug}.json"
    return file

def write_json_file(path,json_data):

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    return path

def extract_json_data(json_dict):

    title = json_dict.get("title", "untitled")
    url = json_dict.get("url", "")
    source = json_dict.get("source", "")
    run_id = json_dict.get("run_id", "")

    return {
        "title": title,
        "url": url,
        "source": source,
        "run_id": run_id
    }

def save_json(json_data, domain, title, base_path=None):

    if base_path is None:
        base_path = Path("data")
    else:
        base_path = Path(base_path)

    file_path = resolve_output_path(title, domain, base_path)

    written_path = write_json_file(file_path, json_data)

    return written_path

def find_json_files(folder_path):
    from pathlib import Path

    base = Path(folder_path)

    if not base.exists():
        return []

    results = []

    for sub in base.iterdir():
        if sub.is_dir():
            for file in sub.rglob("*.json"):  # rglob = recursive
                results.append(file)

    return results