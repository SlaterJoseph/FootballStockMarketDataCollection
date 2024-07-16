import os

import yaml


def yaml_lookup(lookup_val: str) -> str:
    """
    A function which does yaml lookup
    :param lookup_val: The value to be looked up
    :return: The looked up value
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    yaml_path = os.path.join(root_dir, 'properties.yaml')

    with open(yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

    return yaml_data[lookup_val] if not None else None