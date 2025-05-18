# GetReadyToWork

GetReadyToWork is a python script originally created to free its user from the repetitive daily task of launching every app he needs on its machine before being able to work.
For exemple, a programmer would tipically start the day by launching his mailing app, his favorite browser, an IDE, a git GUI or whatever, before being able or willing to work.
----> What about doing it all with one click and go fetch some coffee instead ?

GetReadyToWork lets you launch your favorite applications in one click, with a modern, multi-language, cross-platform interface (Windows, macOS, Linux).


## Main Features
- **Graphical selection of applications to launch** (search, disk grouping)
- **Configurable scan folders** for automatic detection
- **Manual selection from all installed applications** (independent from scan folders, works on every OS)
- **Multi-language** (French/English, auto-detection)
- **Modern and responsive UI** (loader during scans, robust error handling, etc.)
- **Robust configuration** (auto-save, per-OS scan paths)

## Installation

### Prerequisites
- Python 3.10+ (for source version)
- [winapps](https://pypi.org/project/winapps/) (Windows only, for full detection of installed applications)

### Using the Installer (Recommended)
1. Download the release archive for your OS (`build/v0.0.3/` folder or `.zip` from GitHub Releases)
2. Extract it wherever you want
3. If you want to generate the executables folder yourself, run:
   - **Windows:** `python setup.py build --build-exe build/v0.0.3`
   - **macOS/Linux:** `python3 setup.py build --build-exe build/latest`
   - The generated executables will be in the `build/v0.0.3` (Windows) or `build/latest` (macOS/Linux) folder. On macOS/Linux, you may need to make the file executable with `chmod +x build/latest/GetReadyToWork` and run it with `./GetReadyToWork`.
4. Run the appropriate launcher for your OS:
   - **Windows:** `GetReadyToWork.exe` or `ParametrageGetReadyToWork.exe`
   - **macOS/Linux:**
     - `python3 src/app_launcher/GetReadyToWork.py` (launcher)
     - `python3 src/app_configurator/ParametrageGetReadyToWork.py` (configuration)
     - Or run the generated executable from `build/latest/` if you built it as above.

### From Source
1. Clone the repository
2. Install dependencies:
   - Windows: `pip install -r installers/requirements-windows.txt`
   - Linux/Mac: `pip install -r installers/requirements-linux.txt`
   - (On Windows, also run: `pip install winapps`)
3. Run:
   - `python src/app_launcher/GetReadyToWork.py` (launcher)
   - `python src/app_configurator/ParametrageGetReadyToWork.py` (configuration)

## Usage

### Recommended (development):
- **Launcher:**
  - `python -m src.app_launcher.GetReadyToWork`
- **Configuration GUI:**
  - `python -m src.app_configurator.ParametrageGetReadyToWork`

### Frozen executables (Windows):
- `GetReadyToWork.exe` (main launcher)
- `ParametrageGetReadyToWork.exe` (configuration GUI)

## Project Structure
- `src/app_launcher/` : Main launcher app (`GetReadyToWork.py`)
- `src/app_configurator/` : GUI for selecting/configuring apps to launch (`ParametrageGetReadyToWork.py`, `GUI.py`)
- `src/common/` : Shared modules/utilities (`utils.py`, `config_manager.py`)
- `src/config/` : Configuration and resource files (i18n, etc.)
- `src/runtime/` : User config and runtime-generated files (`apps_to_launch.json`, logs, etc.)

## Configuration Management
- All configuration file access is centralized in `src/common/config_manager.py`.
- All shared utilities are in `src/common/utils.py`.
- GUI code is in `src/app_configurator/GUI.py`.

## Notes
- For full detection of installed applications on Windows, the Python module `winapps` must be installed (`pip install winapps`).
- See `HOW TO.txt` for build instructions and advanced usage.

---

**For questions or contributions, open an issue or pull request on GitHub!**


---
Authored by Samuel VANNIER






