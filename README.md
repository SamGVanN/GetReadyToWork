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

## Important Notes
- **Windows**: For full detection of installed applications, the Python module `winapps` must be installed (`pip install winapps`).
- **macOS/Linux**: Detection uses system standards (Applications, .desktop files, packages).
- User configuration files are in the `runtime/` folder.

## Recommended Structure
```
GetReadyToWork/
├── src/                # Python source code
├── runtime/            # User config/data files
├── installers/         # Install scripts and requirements
├── build/              # Build artifacts (should be gitignored)
├── setup.py, README.md, ...
```

## Changelog
See `CHANGELOG.md` for the full list of features and fixes.

---

**For questions or contributions, open an issue or pull request on GitHub!**


---
Authored by Samuel VANNIER






