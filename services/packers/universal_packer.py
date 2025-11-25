
from schemas.mappers.music_mapper import map_music_data
from utils.json_handler import save_json

DOMAIN_MAPPERS = {
    "music": map_music_data
}

def pack_data(domain, title, extracted_data, url, source, run_id):

    mapper = DOMAIN_MAPPERS[domain]

    schema_obj = mapper(title, extracted_data, url, source, run_id)

    json_text = schema_obj.model_dump_json(indent=2, ensure_ascii=False)

    return save_json(json_text, domain, title)