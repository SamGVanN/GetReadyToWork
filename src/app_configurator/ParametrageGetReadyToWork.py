import sys
import os
import logging
import locale

# Always use absolute import for GUI
try:
    from src.app_configurator.GUI import AppConfigurator
except ImportError:
    try:
        from app_configurator.GUI import AppConfigurator
    except ImportError:
        # Fallback for frozen or direct execution
        import importlib.util
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        gui_path = os.path.join(exe_dir, 'app_configurator', 'GUI.py')
        if not os.path.exists(gui_path):
            gui_path = os.path.join(os.path.dirname(__file__), 'GUI.py')
        spec = importlib.util.spec_from_file_location('app_configurator.GUI', gui_path)
        gui_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gui_mod)
        AppConfigurator = gui_mod.AppConfigurator

if __name__ == "__main__":
    app = AppConfigurator()
    app.mainloop()
