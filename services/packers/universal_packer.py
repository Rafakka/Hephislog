
from utils.json_handler import save_json

def pack_data(domain: str, validated_object):
    """
    Convert a validated Pydantic object into JSON and save it.
    Takes only the domain and the validated object.
    """

    json_dict = validated_object.model_dump()

    title = json_dict.get("title", "untitled")
    url = json_dict.get("url", "")
    source = json_dict.get("source", "")
    run_id = json_dict.get("run_id", "")

    file_path = save_json(
        json_data=json_dict,
        domain=domain,
        title=title
    )

    return {
        "path": file_path,
        "domain": domain,
        "title": title,
        "url": url,
        "source": source,
        "run_id": run_id
    }