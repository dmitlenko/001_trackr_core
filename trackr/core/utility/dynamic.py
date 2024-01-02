

def nested_dict_to_list(d: dict, keys: list) -> list[dict]:
    result = []

    if len(keys) == 1:
        for key, value in d.items():
            result.append({keys[0] + "_id": key, keys[0]: value})
    else:
        for key, value in d.items():
            for item in nested_dict_to_list(value, keys[1:]):
                item[keys[0] + "_id"] = key
                item[keys[0]] = value
                result.append(item)

    return result
