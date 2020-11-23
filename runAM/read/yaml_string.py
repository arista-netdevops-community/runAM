import yaml

def yaml_string(a_string, load_all=False):
    if not load_all:
            yaml_data = yaml.load(a_string, Loader=yaml.FullLoader)
    else:
        yaml_data = list(yaml.load_all(a_string, Loader=yaml.FullLoader))  # convert generator to list before returning
    return yaml_data
