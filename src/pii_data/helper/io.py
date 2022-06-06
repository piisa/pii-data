from yaml import load as yaml_load, SafeLoader as YamlLoader

from typing import Dict

def load_yaml(filename: str) -> Dict:
    with open(filename, encoding='utf-8') as f:
        return yaml_load(f, Loader=YamlLoader)
