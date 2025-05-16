#-------------------------
#  Author: Samuel VANNIER
#-------------------------
# GetReadyToWork est un script python
#
# Il permet de lancer les applications souhaitee
# en un seul clic (ou appel de script)

# Ce script a été créé initialement pour gagner du temps au début de chaque journée de travail et surtout
# se libérer de la simple tâche répétitive de lancer les mêmes applications une par une tous les matins
# C'est pas grand chose, mais je préfere utiliser ces quelques secondes pour me faire un café =D

# Libre à chacun de proposer des améliorations et de le faire évoluer à sa guise

# Pour ajouter une application à la liste des app
# il suffit de l'ajouter dans AppsToExecute avec le chemin de l'application en question 
##################################################################################################


# This is the main launcher script for GetReadyToWork (app_launcher)
import os, sys, subprocess, logging
import locale
import json
from time import sleep
from datetime import datetime
import importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'config')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

# Try to import i18n_resources from config or flat, for both source and frozen modes
try:
    if getattr(sys, 'frozen', False):
        # In frozen mode, look for i18n_resources in the same directory as the executable
        import importlib.util
        exe_dir = os.path.dirname(sys.executable)
        i18n_path = os.path.join(exe_dir, 'i18n_resources.py')
        if os.path.exists(i18n_path):
            spec = importlib.util.spec_from_file_location('i18n_resources', i18n_path)
            i18n_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(i18n_mod)
        else:
            # fallback to importlib (for cx_Freeze zipped builds)
            i18n_mod = importlib.import_module('i18n_resources')
    else:
        try:
            i18n_mod = importlib.import_module('config.i18n_resources')
        except ImportError:
            i18n_mod = importlib.import_module('i18n_resources')
except Exception as e:
    print(f"[FATAL] Could not import i18n_resources: {e}")
    sys.exit(1)
messages = i18n_mod.messages
messages_fr = i18n_mod.messages_fr

# Language detection
lang = locale.getdefaultlocale()[0]
if lang and lang.startswith('fr'):
    _ = messages_fr
else:
    _ = messages

# Always write logs to a file in the same directory as the executable (build or src)
def get_log_path():
    if getattr(sys, 'frozen', False):
        # Running as a bundled exe
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'logs.log')

logging.basicConfig(filename=get_log_path(), encoding='utf-8', level=logging.DEBUG, force=True)

# Robustly resolve runtime directory for config files
if getattr(sys, 'frozen', False):
    # In frozen mode, runtime files are in the same dir as the executable
    runtime_dir = os.path.dirname(sys.executable)
else:
    runtime_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'runtime'))

# Ensure runtime directory exists (for writing, if needed)
os.makedirs(runtime_dir, exist_ok=True)

CONFIG_FILE = os.path.join(runtime_dir, 'apps_to_launch.json')
DEFAULT_FILE = os.path.join(runtime_dir, 'default.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        AppsToExecute = json.load(f)
elif os.path.exists(DEFAULT_FILE):
    with open(DEFAULT_FILE, 'r', encoding='utf-8') as f:
        AppsToExecute = json.load(f)
else:
    AppsToExecute = ["outlook"]

def open_file(appName):
    if sys.platform == "win32":
        try:
            os.startfile(appName)
        except Exception as e:
            logging.error(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Failed launching app: {appName} | {e}")
    else:
        try:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, appName])
        except Exception as e:
            logging.error(f"Failed launching app: {appName} | {e}")

print(_["go_coffee"])
for app in AppsToExecute:
    sleep(0.5)
    open_file(app)
print(_["ready"])
print(_["see_you"])
