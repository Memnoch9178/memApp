import yaml

def load_yaml(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def dump_yaml(data, path: str):
    with open(path, 'w') as f:
        yaml.safe_dump(data, f)
