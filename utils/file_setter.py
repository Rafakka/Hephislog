import os
import json

def file_finder(folder_name: str):

    if os.path.exists(folder_name):
        file_path = None
        data = None

        for root, _, files in os.walk(folder_name):
            for file in files:
                if file.endswith('.json'):
                    candidate = os.path.join(root, file)
                    try:
                        with open(candidate, 'r', encoding='utf-8') as f:
                            loaded = json.load(f)
                            if isinstance(loaded, dict):
                                file_path = candidate
                                data = loaded
                                break
                    except (json.JSONDecodeError, OSError):
                        return {
                            "success": False,
                            "file_path": None,
                            "data": None,
                            "error": "JSONDecodeError",
                            "message": f"Error reading JSON file: {candidate}"
                        }

            if file_path is not None:
                break
        if file_path is None:
            return {
                "success": False,
                "file_path": None,
                "data": None,
                "error": "FilePathNotFound",
                "message": "Did not find any valid JSON file."
            }
        return {
            "success": True,
            "file_path": file_path,
            "data": data,
            "error": None,
            "message": "Data found."
        }
    else:
        return {
            "success": False,
            "file_path": None,
            "data": None,
            "error": "FolderNotExist",
            "message": f"Folder '{folder_name}' does not exist."
        }
