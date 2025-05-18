from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = None

executables = [
    Executable("src/app_launcher/GetReadyToWork.py", base=base, target_name="GetReadyToWork.exe"),
    Executable("src/app_configurator/ParametrageGetReadyToWork.py", base=base, target_name="ParametrageGetReadyToWork.exe")
]

# List all packages and files needed
packages = ["idna", "winapps", "tkinter", "ctypes", "json", "locale"]
include_files = [
    ("src/config/i18n_resources.py", "i18n_resources.py"),
    ("src/config/scan_paths_windows.py", "scan_paths_windows.py"),
    ("src/config/scan_paths_mac.py", "scan_paths_mac.py"),
    ("src/config/scan_paths_linux.py", "scan_paths_linux.py"),
    ("src/config/scan_paths_user.json", "scan_paths_user.json"),
    ("runtime/default.json", "default.json"),
    ("runtime/apps_to_launch.json", "apps_to_launch.json"),
    ("src/common/utils.py", "common/utils.py"),  # Seul utils.py dans un dossier common
    ("src/common/config_manager.py", "common/config_manager.py"),  # Ajouté pour centraliser la gestion de config
    ("src/common/__init__.py", "common/__init__.py"),  # Pour que common soit un package
]

options = {
    'build_exe': {    
        'packages': packages,
        'includes': ['winapps'],
        'include_files': include_files,
        'include_msvcr': True,
        'excludes': ['unittest', 'email', 'html', 'http', 'xmlrpc', 'pydoc_data', 'test'],
    },
}


setup(
    name = "Get Ready To Work",
    options = options,
    version = "0.0.3",
    description = 'GetReadyToWork lets you launch your favorite apps in one click, with multi-language and cross-platform support. Requires winapps on Windows for full app detection.',
    executables = executables
)

# NOTE: Pour la détection complète des applications installées sous Windows, le module Python 'winapps' doit être installé (pip install winapps). Voir README.md pour plus d'infos.