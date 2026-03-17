def flatten_json(nested, parent_key="", result=None):
    if result is None:
        result = {}
    for key, value in nested.items():
        # build new key → parent_key + "_" + key
        # if value is dict → recurse
        # else → store in result

        new_key = parent_key + "_" + key if parent_key else key

        if isinstance(value, dict):
            flatten_json(value, new_key, result)
        else:
            result[new_key] = value
    return result

nested = {
    "patient_id": "P123",
    "name": "John",
    "conditions": {
        "primary": {
            "disease": "diabetes",
            "severity": {
                "level": "high",
                "score": 8
            }
        }
    }
}

print(flatten_json(nested))