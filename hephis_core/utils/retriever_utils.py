from pathlib import Path
from hephis_core.utils.file_setter import file_finder


def load_from_local(base: Path, slug: str) -> dict | None:
    """
    Load a single processed item located in:
        base/<slug>/
    Example:
        data/music/<slug>/
        data/recipes/<slug>/
    """
    folder = base / slug

    if not folder.exists() or not folder.is_dir():
        return None

    info = file_finder(str(folder))

    if info and info.get("success"):
        return info["data"]

    return None


def list_local(base: Path) -> list:
    """
    List all processed items in a given domain.
    Example:
        base = Path("data/music")  -> returns all music entries
    """
    results = []

    if not base.exists() or not base.is_dir():
        return results

    for folder in base.iterdir():
        if folder.is_dir():
            info = file_finder(str(folder))

            if info.get("success"):
                data = info["data"]
                results.append({
                    "title": data.get("title", "Unknown"),
                    "slug": folder.name,
                    "path": info["file_path"]
                })

    return results