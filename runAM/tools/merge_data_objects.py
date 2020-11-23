def merge_data_objects(d1, d2, deduplicate_lists=True, merge_dict_in_lists=False):
    """A very simple function to merge 2 data objects into one recursively

    Args:
        d1 (dict or list): Original data object.
        d2 (dict or list): Data object to merge. Has higher priority in case of conflicting keys.
        deduplicate_lists (bool, optional): Remove duplicate elements from the list. Defaults to True.
        merge_dict_in_lists (bool, optional): Merge dictionaries from d2 into lists from d1. Defaults to False.

    Returns:
        dict or list: Merged data.
    """
    # a very simple function to merge 2 data objects into one recursively
    if isinstance(d1, dict) and isinstance(d2, dict):
        result = dict()
        all_keys = set(d1.keys()).union(d2.keys())
        for key in all_keys:
            if key not in d1.keys():
                result[key] = d2[key]
            elif key not in d2.keys():
                result[key] = d1[key]
            else:
                result[key] = merge_data_objects(d1[key], d2[key])
    elif isinstance(d1, list) and isinstance(d2, list):
        if deduplicate_lists:
            if merge_dict_in_lists:
                result = list()
                temp_dict = dict()
                for element in d1 + d2:
                    if isinstance(element, dict):
                        temp_dict = merge_data_objects(temp_dict, element)
                    else:
                        if element not in result:
                            result.append(element)
                result.append(temp_dict)
            else:
                result = list()
                for element in d1 + d2:
                    if element not in result:
                        result.append(element)
        else:
            result = d1 + d2
    else:  # 2nd object has higher priority if objects are different or not dict/list/str type
        result = d2

    return result
