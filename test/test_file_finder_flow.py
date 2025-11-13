from utils.file_setter import file_finder


def test_file_finder_flow():
    # Use the folder where your json is
    result = file_finder(folder_name="recipes_tg")

    print("\n--- FILE FINDER RESULT ---")
    print(result)

    # Basic checks
    assert result["success"] is True, "File finder failed to locate a valid JSON file."

    print("\n--- FOUND FILE PATH ---")
    print(result["file_path"])

    print("\n--- RAW JSON CONTENT ---")
    print(result["data"])
