import os
import json
import sys

# Détermination robuste des chemins de fichiers runtime/config

def get_runtime_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, '..', '..', 'runtime'))

def get_config_file():
    return os.path.join(get_runtime_dir(), 'apps_to_launch.json')

def get_default_file():
    return os.path.join(get_runtime_dir(), 'default.json')

def load_config():
    config_file = get_config_file()
    default_file = get_default_file()
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif os.path.exists(default_file):
        with open(default_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return ["outlook"]

def save_config(data):
    config_file = get_config_file()
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Pour scan_paths_user.json

def get_scan_paths_file():
    if getattr(sys, 'frozen', False):
        return os.path.join(get_runtime_dir(), 'scan_paths_user.json')
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_dir, '..', '..', 'config', 'scan_paths_user.json'))

def load_scan_paths():
    scan_file = get_scan_paths_file()
    if os.path.exists(scan_file):
        with open(scan_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_scan_paths(paths):
    scan_file = get_scan_paths_file()
    os.makedirs(os.path.dirname(scan_file), exist_ok=True)
    with open(scan_file, 'w', encoding='utf-8') as f:
        json.dump(paths, f, indent=2)
