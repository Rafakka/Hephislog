from pathlib import Path
from hephis_core.infra.retrievers.registry import retriever
from hephis_core.utils.retriever_utils import load_from_local, list_local
from hephis_core.utils.logger_decorator import log_action

BASE = Path("data/music")


@log_action(action="retrieve_music_from_local")
@retriever(domain="music", input_type="file")
def load_music(slug: str):
    return load_from_local(BASE, slug)


@log_action(action="list_local_music")
@retriever(domain="music", input_type="list")
def list_music(_: str = ""):
    return list_local(BASE)