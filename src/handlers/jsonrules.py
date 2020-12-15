"""
jsonrules.py

JSON rules loader for the server handlers

___________________

by:
Ayzurus
"""
import json

_root_path = "./"


def setup(path: str):
    """sets up the working path to find the json files"""
    global _root_path
    _root_path = path


def get(proto: str):
    """obtain the json rules for the given protocol"""
    json_rules = {}
    with open(_root_path + proto + ".json", "r") as rules:
        json_rules = json.load(rules)
    return json_rules
