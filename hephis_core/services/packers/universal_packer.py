
from services.cleaners.data_cleaner import slugify
from utils.json_handler import serialize_json, extract_json_data, save_json

def pack_data(domain: str, validated_object):
    """
    Convert a validated Pydantic object into JSON and save it.
    Takes only the domain and the validated object.
    """
    json_dict = serialize_json(validated_object)

    metadata = extract_json_data (json_dict)

    file_path = save_json(
        json_data=json_dict,
        domain=domain,
        title=metadata["title"]
    )

    return {
        "path": file_path,
        "domain": domain,
        **metadata
    }