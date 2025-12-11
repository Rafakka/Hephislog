import importlib
import pkgutil
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent
PACKAGE_NAME = __package__

def autodiscover_retrievers():

    for module_info in pkgutil.walk_packages(
        path=[str(PACKAGE_ROOT)],
        prefix=PACKAGE_NAME + "."
    ):
        module_name = module_info.name

        if module_name.endswith(".registry") or module_name.endswith(".loader"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as exc:
            print(f"[Extractor Loader] Failed to import {module_name}: {exc}")