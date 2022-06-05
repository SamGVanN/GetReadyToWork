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


#################################################
#Imports and config
import os, sys, subprocess, logging
if sys.platform == "win32":
        import winapps

from time import sleep


logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)
#################################################



#################################################
#Applications to start when using GetReadyToWork:
AppsToExecute = [
    "outlook",
    "Opera",
    "Code",
    "Fork"
]
#################################################




#OS based method to launch an app
def open_file(appName):
    if sys.platform == "win32":
        try:
            os.startfile(appName)
        except:
            logging.error(f"Failed launching app: "+appName)
    else:
        try:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, appName])
        except :
            logging.error(f"Failed launching app: "+appName)




#region main()
for app in AppsToExecute:
    sleep(0.5)
    open_file(app)



