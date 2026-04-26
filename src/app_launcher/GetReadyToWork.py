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
import os
import sys
import logging
import locale
from time import sleep
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.common.utils import setup_logging, load_apps_to_execute, launch_app
from src.common.config_manager import get_config_file
from src.config import i18n_resources

setup_logging()
logging.info('--- Lancement GetReadyToWork.py ---')

# Robustly resolve config file path
CONFIG_FILE = get_config_file()

# Load the list of apps to execute
AppsToExecute = load_apps_to_execute(CONFIG_FILE)

# i18n messages
lang = locale.getdefaultlocale()[0]
if lang and lang.startswith('fr'):
    _ = i18n_resources.messages_fr
else:
    _ = i18n_resources.messages

print(_["go_coffee"] if "go_coffee" in _ else "Launching your apps...")
for app in AppsToExecute:
    sleep(0.5)
    launch_app(app)
print(_["ready"] if "ready" in _ else "All apps launched!")
print(_["see_you"] if "see_you" in _ else "See you!")
