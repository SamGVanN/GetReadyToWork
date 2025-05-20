from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use Win32GUI to hide console on Windows

# Common files to be included across all platforms
common_include_files = [
    ("src/config/i18n_resources.py", "i18n_resources.py"),
    ("src/config/scan_paths_windows.py", "scan_paths_windows.py"),
    ("src/config/scan_paths_mac.py", "scan_paths_mac.py"),
    ("src/config/scan_paths_linux.py", "scan_paths_linux.py"),
    ("src/config/scan_paths_user.json", "scan_paths_user.json"),
    ("runtime/default.json", "default.json"),
    ("runtime/apps_to_launch.json", "apps_to_launch.json"),
    ("src/common/utils.py", "common/utils.py"),
    ("src/common/config_manager.py", "common/config_manager.py"),
    ("src/common/__init__.py", "common/__init__.py"),
]

# --- Platform-specific configurations ---

if sys.platform == "win32":
    executables = [
        Executable("src/app_launcher/GetReadyToWork.py", base=base, target_name="GetReadyToWork.exe"),
        Executable("src/app_configurator/ParametrageGetReadyToWork.py", base=base, target_name="ParametrageGetReadyToWork.exe")
    ]
    packages = ["idna", "tkinter", "ctypes", "json", "locale", "winapps", "pywin32"]
    build_exe_options = {
        'packages': packages,
        'include_files': common_include_files,
        'include_msvcr': True,
        'excludes': ['unittest', 'email', 'html', 'http', 'xmlrpc', 'pydoc_data', 'test'],
    }
    options = {'build_exe': build_exe_options}

elif sys.platform == "darwin":  # macOS
    executables = [
        Executable("src/app_launcher/GetReadyToWork.py", target_name="GetReadyToWork"),
        Executable("src/app_configurator/ParametrageGetReadyToWork.py", target_name="ParametrageGetReadyToWork")
    ]
    packages = ["idna", "tkinter", "ctypes", "json", "locale"]
    # For macOS, include_files paths are relative to Contents/Resources within the .app bundle
    macos_include_files = [(src, f"../Resources/{dst}") for src, dst in common_include_files]

    build_exe_options = { # build_exe is used by bdist_mac
        'packages': packages,
        'include_files': macos_include_files, # common_include_files, # Adjusted for .app structure
        'excludes': ['unittest', 'email', 'html', 'http', 'xmlrpc', 'pydoc_data', 'test', 'winapps', 'pywin32'],
        'iconfile': 'src/app_launcher/icon.icns', # Assuming you have an icon
    }
    bdist_mac_options = {
        'bundle_name': 'Get Ready To Work', # This will create "Get Ready To Work.app"
        'iconfile': 'src/app_launcher/icon.icns', # Specify icon for the .app bundle
        # 'plist_items': [('PYAPP_VERSION', '0.0.3')] # Example Info.plist item
    }
    options = {
        'build_exe': build_exe_options,
        'bdist_mac': bdist_mac_options,
    }


elif sys.platform.startswith("linux"):  # Linux
    executables = [
        Executable("src/app_launcher/GetReadyToWork.py", target_name="GetReadyToWork"),
        Executable("src/app_configurator/ParametrageGetReadyToWork.py", target_name="ParametrageGetReadyToWork")
    ]
    packages = ["idna", "tkinter", "ctypes", "json", "locale"]
    build_exe_options = {
        'packages': packages,
        'include_files': common_include_files, # Files will be in 'lib/appname/' alongside executables
        'excludes': ['unittest', 'email', 'html', 'http', 'xmlrpc', 'pydoc_data', 'test', 'winapps', 'pywin32'],
    }
    bdist_appimage_options = {
        'appimage_path': 'GetReadyToWork.AppImage', # Name of the output AppImage
        # 'pre_apprun_hook': 'pre_apprun_hook.sh', # Optional hook script
    }
    options = {
        'build_exe': build_exe_options,
        'bdist_appimage': bdist_appimage_options,
    }

else:
    # Fallback for other platforms or if platform detection fails
    executables = [
        Executable("src/app_launcher/GetReadyToWork.py"),
        Executable("src/app_configurator/ParametrageGetReadyToWork.py")
    ]
    packages = ["idna", "tkinter", "ctypes", "json", "locale"]
    build_exe_options = {
        'packages': packages,
        'include_files': common_include_files,
        'excludes': ['unittest', 'email', 'html', 'http', 'xmlrpc', 'pydoc_data', 'test', 'winapps', 'pywin32'],
    }
    options = {'build_exe': build_exe_options}


setup(
    name="Get Ready To Work",
    version="0.0.4", # Incremented version
    description='GetReadyToWork lets you launch your favorite apps in one click, with multi-language and cross-platform support.',
    executables=executables,
    options=options
)

# NOTE: For full app detection on Windows, 'winapps' & 'pywin32' are needed.
# For macOS, ensure 'icon.icns' exists at 'src/app_launcher/icon.icns' or remove iconfile options.
# For Linux AppImage, 'patchelf' might be required.
# Build commands:
# python setup.py build_exe  (Windows or generic)
# python setup.py bdist_mac  (macOS)
# python setup.py bdist_appimage (Linux)