
import hephis_core.infra.extractors
from hephis_core.infra.extractors.registry import EXTRACTOR_REGISTRY

print(EXTRACTOR_REGISTRY)

# import pkgutil
# import hephis_core.infra.extractors

# print([m.name for m in pkgutil.iter_modules(hephis_core.infra.extractors.__path__)])