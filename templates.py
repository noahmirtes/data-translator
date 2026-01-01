# templates.py

from dataclasses import dataclass
import json


@dataclass
class DataTemplate:
    name : str
    version : str
    header_map : list[str, str]
    post_processes : list

def load_json(template_path):
    with open(template_path, 'r') as f:
        return json.load(f)

def extract_template_structure(template_path, template_name) -> DataTemplate:
    """Load the template specific structure from a json file"""
    all_templates = load_json(template_path)
    raw_template = all_templates[template_name]

    data_template = DataTemplate(
        name = raw_template['name'],
        version = raw_template['version'],
        header_map = raw_template['header_map'],
        post_processes = raw_template['post_processes'],
    )

    return data_template
