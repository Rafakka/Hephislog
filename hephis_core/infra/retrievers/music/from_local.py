from pathlib import Path
from hephis_core.infra.retrievers.registry import retriever
from hephis_core.utils.logger_decorator import log_action
from hephis_core.utils.file_setter import file_finder


BASE = Path("data/music")


@log_action(action="retrieve_music_from_local")
@retriever(domain="music", input_type="file")
def load_music_from_local(path: str) -> dict | None:
    """
    Load a music entry stored locally in data/music/<slug>
    """
    folder = BASE / path

    if not folder.exists() or not folder.is_dir():
        return None

    info = file_finder(str(folder))

    if info and info.get("success"):
        return info["data"]

    return None


@log_action(action="list_local_musics")
@retriever(domain="music", input_type="list")
def list_local_musics(_: str = "") -> list:
    """
    List all music folders and return metadata.
    """
    results = []

    for folder in BASE.iterdir():
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