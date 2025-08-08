import yaml
from typing import Any

def load_yaml(path: str):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        print(f"Error loading YAML file: {e}")
        return None

def dump_yaml(data: Any, path: str):
    try:
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
    except OSError as e:
        print(f"Error writing YAML file: {e}")
    except PermissionError:
        print(f"Error: Permission denied - {path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error: YAML parsing error - {e}")
        return None

def dump_yaml(data, path: str):
    try:
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
    except FileNotFoundError:
        print(f"Error: File not found - {path}")
    except PermissionError:
        print(f"Error: Permission denied - {path}")
    except yaml.YAMLError as e:
        print(f"Error: YAML dumping error - {e}")
