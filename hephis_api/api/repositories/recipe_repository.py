from pathlib import Path
from hephis_core.utils.file_setter import file_finder

class RecipeRepository:
    BASE = Path("data/recipes")

    @classmethod
    def load(cls, slug):
        folder = cls.BASE / slug
        return file_finder(str(folder))
    
    @classmethod
    def list(cls):
        results = []
        for folder in cls.BASE.iterdir():
            if folder.is_dir():
                info = file_finder(str(folder))
                if info["success"]:
                    data = info["data"]
                    results.append({
                        "title": data.get("title", "Unknown"),
                        "slug": folder.name,
                        "path": info["file_path"]
                    })
        return results