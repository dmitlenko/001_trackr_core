import json


def dict_items(d: dict, key: str = "", prefix: str = "") -> list[dict]:
    if key:
        d = d[key]

    return [{f"{prefix}_key": k, prefix: v} for k, v in d.items()]


def save_to_file(d: dict, file_path: str):
    with open(file_path, "w") as file:
        file.write(json.dumps(d, indent=4))