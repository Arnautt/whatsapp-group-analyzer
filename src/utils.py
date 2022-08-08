import re
import yaml


def load_config(path):
    """Load YAML configuration file given its path"""
    with open(path) as file:
        config = yaml.safe_load(file)
    return config


def is_message(msg):
    """
    Test if a string is a message. Supposed to be in the following form :
    ===> date - name: message
    """
    return bool(re.search(r'.*-.*:', msg))
