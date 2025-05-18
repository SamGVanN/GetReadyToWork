If you're interested in participating to this project
1) Great news!
2) Thank you
3) Here are some instructions/demands
4) Have fun


This project (tries to) follow ConventionalCommits
https://www.conventionalcommits.org/en/v1.0.0/


If you want to fork this project, feel free to do so and please mention this project :)


Logs:
https://docs.python.org/3/howto/logging.html

============================
Technologies & Project Structure
============================

This project is a cross-platform Python application with a modern GUI for configuring and launching user-selected applications.

Technologies used:
- Python 3.10+
- Tkinter (ttk) for the graphical interface
- cx_Freeze or PyInstaller for packaging executables
- Pillow (PIL) and pywin32 for Windows icon support
- Standard libraries: os, sys, json, locale, logging, threading, ctypes, subprocess
- i18n (multi-language) support via a resource file (`src/config/i18n_resources.py`)

Project structure:
- `src/app_launcher/` : Main launcher app (`GetReadyToWork.py`)
- `src/app_configurator/` : GUI for selecting/configuring apps to launch (`ParametrageGetReadyToWork.py`, `GUI.py`)
- `src/config/` : Configuration and resource files (i18n, etc.)
- `src/common/` : Shared modules/utilities (`utils.py`, `config_manager.py`)
- `src/installers/` : Install scripts and requirements
- `src/runtime/` : User config and runtime-generated files (`apps_to_launch.json`, logs, etc.)

How it works:
- The configurator GUI scans for installed applications, lets the user select which to launch, and saves the selection in `runtime/apps_to_launch.json`.
- The launcher reads this config and launches all selected applications in one click.
- The UI is fully multilingual (English/French) and adapts to the user's OS language.
- The project is designed to be easily portable and maintainable.

## Development & Execution
- Always use `python -m ...` from the project root for both launcher and configurator in development.
- All configuration file access is centralized in `src/common/config_manager.py`.
- All shared utilities are in `src/common/utils.py`.
- GUI code is in `src/app_configurator/GUI.py`.

## Packaging
- Use cx_Freeze or PyInstaller to build executables. All necessary files (including `common/` and config) are included in the build.
- For full detection of installed applications on Windows, the Python module `winapps` must be installed (`pip install winapps`).

See HOW TO.txt for usage and build instructions.