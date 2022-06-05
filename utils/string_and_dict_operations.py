def strip_whitespaces(input_dict: dict) -> dict:
    """Removes all leading and trailing whitespaces from the dict keys and string values"""
    output_dict = {}
    for key, value in input_dict.items():
        if type(value) == str:
            output_dict[key.strip()] = value.strip()
        else:
            output_dict[key.strip()] = value
    return output_dict


def clean_empty(input_dict):
    if isinstance(input_dict, dict):
        return {
            k: v
            for k, v in ((k, clean_empty(v)) for k, v in input_dict.items())
            if v is not None
        }
    if isinstance(input_dict, list):
        return [v for v in map(clean_empty, input_dict) if v is not None]
    return input_dict
