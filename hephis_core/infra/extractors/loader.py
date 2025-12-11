import importlib
import pkgutil
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent
PACKAGE_NAME = __package__   # "hephis_core.infra.extractors"

def autodiscover_extractors():
    """
    Imports all extractor modules inside extractors/* folders.
    Decorators inside those modules will auto-register themselves.
    """
    for module_info in pkgutil.walk_packages(
        path=[str(PACKAGE_ROOT)],
        prefix=PACKAGE_NAME + "."
    ):
        module_name = module_info.name

        # Skip modules
        if module_name.endswith(".registry") or module_name.endswith(".loader"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as exc:
            print(f"[Extractor Loader] Failed to import{module_name}:{exc}")