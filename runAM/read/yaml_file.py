import yaml

def yaml_file(filename, load_all=False):
    with open(filename, mode='r') as f:
        if not load_all:
            yaml_data = yaml.load(f, Loader=yaml.FullLoader)
        else:
            yaml_data = list(yaml.load_all(f, Loader=yaml.FullLoader))  # convert generator to list before returning
    return yaml_data