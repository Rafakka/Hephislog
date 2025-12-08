import json
import logging
from pathlib import Path
import send2trash as stt

from hephis_core.utils.output_manager import get_processed_folder

BASE_PROCESSED_DIR = Path("data")

# -----------------------------------------------------------
# 1. DELETE ONE ENTRY (music/<title>/ or recipes/<title>/)
# -----------------------------------------------------------

def delete_one_entry(domain: str, title: str):

    from hephis_core.utils.logger import log_deletion

    folder = get_processed_folder(domain, title)

    if not folder.exists():
        log_deletion(
            event="Delete entry failed (folder not found)",
            domain=domain,
            title=title,
            path=str(folder),
            dry_run=False,
            success=False,
        )
        return {
            "success": False,
            "file_path": None,
            "error": "NotFound",
            "message": "Error: entry folder not found."
        }

    try:
        stt.send2trash(folder)

        log_deletion(
            event="Deleted entry",
            domain=domain,
            title=title,
            path=str(folder),
            dry_run=False,
            success=True,
        )

        return {
            "success": True,
            "file_path": str(folder),
            "message": "Entry folder was moved to Trash."
        }

    except OSError as e:

        log_deletion(
            event="Delete entry failed (OS error)",
            domain=domain,
            title=title,
            path=str(folder),
            dry_run=False,
            success=False,
            error=str(e),
        )

        return {
            "success": False,
            "file_path": None,
            "error": "OSerror",
            "message": "Error deleting entry folder."
        }


# -----------------------------------------------------------
# 2. DELETE A DOMAIN FOLDER (data/music/ or data/recipes/)
# -----------------------------------------------------------

def delete_data_folder(domain: str, dry_run: bool = False):

    from hephis_core.utils.logger import log_deletion

    folder = BASE_PROCESSED_DIR / domain

    if not folder.exists():
        log_deletion(
            event="Delete domain folder failed (folder not found)",
            domain=domain,
            title=None,
            path=str(folder),
            dry_run=False,
            success=False,
        )
        return {
            "success": False,
            "domain": domain,
            "folder_path": str(folder),
            "error": "NotFound",
            "message": f"Data folder '{domain}' not found."
        }

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

    try:
        stt.send2trash(folder)

        log_deletion(
            event="Deleted domain folder",
            domain=domain,
            title=None,
            path=str(folder),
            dry_run=False,
            success=True,
        )

        return {
            "success": True,
            "dry_run": False,
            "domain": domain,
            "folder_path": str(folder),
            "message": f"Folder '{domain}' was moved to OS trash."
        }

    except OSError as e:

        log_deletion(
            event="Delete domain folder failed (OS error)",
            domain=domain,
            title=None,
            path=str(folder),
            dry_run=False,
            success=False,
            error=str(e),
        )

        return {
            "success": False,
            "dry_run": False,
            "folder_path": str(folder),
            "error": "OSerror",
            "message": f"Error deleting folder: {e}"
        }


# -----------------------------------------------------------
# 3. DELETE ALL (wipe the entire data/ directory)
# -----------------------------------------------------------

def delete_all(dry_run: bool = False):

    from hephis_core.utils.logger import log_deletion

    folder = BASE_PROCESSED_DIR

    if not folder.exists():
        log_deletion(
            event="Delete all failed (folder not found)",
            domain="all",
            title=None,
            path=str(folder),
            dry_run=False,
            success=False,
        )
        return {
            "success": False,
            "error": "NotFound",
            "message": f"Data folder not found."
        }

    if dry_run:
        items = [str(p) for p in folder.rglob("*")]
        return {
            "success": True,
            "dry_run": True,
            "folder_path": str(folder),
            "items_to_delete": items,
            "message": f"Dry-run: Would delete {len(items)} items."
        }

    try:
        stt.send2trash(folder)

        log_deletion(
            event="Deleted all data",
            domain="all",
            title=None,
            path=str(folder),
            dry_run=False,
            success=True,
        )

        return {
            "success": True,
            "dry_run": False,
            "folder_path": str(folder),
            "message": f"Everything was sent to trash."
        }

    except OSError as e:

        log_deletion(
            event="Delete all failed (OS error)",
            domain="all",
            title=None,
            path=str(folder),
            dry_run=False,
            success=False,
            error=str(e),
        )

        return {
            "success": False,
            "dry_run": False,
            "folder_path": str(folder),
            "error": "OSerror",
            "message": f"Deleting all data failed: {e}"
        }
