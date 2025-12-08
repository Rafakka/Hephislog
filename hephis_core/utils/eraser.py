import json
from pathlib import Path
import send2trash as stt

from hephis_core.utils.output_manager import get_processed_folder


BASE_PROCESSED_DIR = Path("data")

def delete_one_entry(domain: str, title: str) -> Path:

    folder = get_processed_folder(domain, title)

    if not folder.exists():
        return {
                    "success": False,
                    "file_path": None,
                    "error": "OSerror",
                    "message": f"Error folder/file not found."
                }

    try:
        stt.send2trash(folder)
        return {
                "success": True,
                "message": f"Entry folder was moved to trash."
                }
    except (OSError):
        return {
                    "success": False,
                    "file_path": None,
                    "error": "OSerror",
                    "message": f"Error reading file."
                }

def delete_data_folder(domain: str, dry_run: bool = False):
    """
    Deletes the entire data/<domain>/ folder.
    If dry_run=True, returns what WOULD be deleted without deleting anything.
    """

    folder = BASE_PROCESSED_DIR / domain

    if not folder.exists():
        return {
            "success": False,
            "domain": domain,
            "folder_path": str(folder),
            "error": "NotFound",
            "message": f"Data folder '{domain}' not found."
        }

    # -------------------------------
    # DRY-RUN MODE
    # -------------------------------
    if dry_run:
        items = [str(p) for p in folder.rglob("*")]
        return {
            "success": True,
            "dry_run": True,
            "domain": domain,
            "folder_path": str(folder),
            "items_to_delete": items,
            "message": f"Dry-run: Would delete {len(items)} items."
        }

    # -------------------------------
    # ACTUAL DELETE (send to trash)
    # -------------------------------
    try:
        stt.send2trash(folder)
        return {
            "success": True,
            "dry_run": False,
            "domain": domain,
            "folder_path": str(folder),
            "message": f"Folder '{domain}' was moved to OS trash."
        }

    except OSError as e:
        return {
            "success": False,
            "dry_run": False,
            "folder_path": str(folder),
            "error": "OSerror",
            "message": f"Error deleting folder: {e}"
        }

def delete_all(dry_run: bool = False):
    """
    Deletes the entire data/ folder.
    If dry_run=True, returns what WOULD be deleted without deleting anything.
    """

    folder = BASE_PROCESSED_DIR

    if not folder.exists():
        return {
            "success": False,
            "error": "NotFound",
            "message": f"Data folder not found."
        }

    # -------------------------------
    # DRY-RUN MODE
    # -------------------------------
    if dry_run:
        items = [str(p) for p in folder.rglob("*")]
        return {
            "success": True,
            "dry_run": True,
            "folder_path": str(folder),
            "items_to_delete": items,
            "message": f"Dry-run: Would delete {len(items)} items."
        }

    # -------------------------------
    # ACTUAL DELETE (send to trash)
    # -------------------------------
    try:
        stt.send2trash(folder)
        return {
            "success": True,
            "dry_run": False,
            "folder_path": str(folder),
            "message": f"Everthing was sent to trash."
        }

    except OSError as e:
        return {
            "success": False,
            "dry_run": False,
            "folder_path": str(folder),
            "error": "OSerror",
            "message": f"Error deleting folder: {e}"
        }