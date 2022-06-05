from cx_Freeze import setup, Executable
base = None
executables = [Executable("src/GetReadyToWork.py", base=base)]

#Renseignez ici la liste complète des packages utilisés par votre application
packages = ["idna"]

options = {
    'build_exe': {    
        'packages':packages,
    },
}


setup(
    name = "Get Ready To Work",
    options = options,
    version = "1.0",
    description = 'GetReadyToWork permet de lancer les applications souhaitée en un seul clic ',
    executables = executables
)