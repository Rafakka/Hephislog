from hephis_core.utils.json_handler import serialize_json, extract_json_data
from hephis_core.utils.output_manager import write_processed_json
from hephis_core.utils.logger_decorator import log_action

@log_action(action="pack data", meta_fields=["domain"])
def pack_data(domain: str, validated_object):
    """
    Serialize, extract metadata, and save processed JSON using the new output manager.
    """
    # Turn Pydantic object into dict
    json_dict = serialize_json(validated_object)

    # Extract metadata (title, url, etc.)
    metadata = extract_json_data(json_dict)

    # Write using the unified output manager
    file_path = write_processed_json(
        domain=domain,
        title=metadata["title"],
        json_dict=json_dict
    )

    return {
        "path": file_path,
        "domain": domain,
        **metadata
    }
