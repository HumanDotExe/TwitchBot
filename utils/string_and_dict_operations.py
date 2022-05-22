def strip_whitespaces(input_dict: dict) -> dict:
    """Removes all leading and trailing whitespaces from the dict keys and string values"""
    output_dict = {}
    for key, value in input_dict.items():
        if type(value) == str:
            output_dict[key.strip()] = value.strip()
        else:
            output_dict[key.strip()] = value
    return output_dict
