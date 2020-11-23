def change_nested_value(path, in_data, new_value=dict(), delete=False):
    """Change a value indexed by a key list.
    Example: change_nested_value(['k1', 0, 'k2'], some_data, some_value) is equal to
                some_data['k1'][0]['k2'] = some_value

    Args:
        path (list): List of keys or list indexes to find the path in nested data structure.
        in_data (dict|list): Input data to be changed.
        new_value (any): Value to be set.
        delete (bool, optional): Delete the element instead of changing the value. Defaults to False.

    Returns:
        dict|list: Updated data.
    """
    path_copy = path.copy()  # to avoid changing original list
    a_key = path_copy.pop(0)
    out_data = in_data.copy()
    if not len(path_copy):
        if delete:
            del out_data[a_key]
        else:
            out_data[a_key] = new_value
    else:
        out_data[a_key] = change_nested_value(path_copy, in_data[a_key], new_value, delete=delete)
    return out_data
