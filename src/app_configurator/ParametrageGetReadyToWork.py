import sys
import os
import logging
import locale
from .GUI import AppConfigurator

try:
    from ..common.utils import get_log_path, setup_logging
except ImportError:
    import importlib.util
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    utils_path = os.path.join(exe_dir, 'common', 'utils.py')
    spec = importlib.util.spec_from_file_location('common.utils', utils_path)
    utils_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utils_mod)
    get_log_path = utils_mod.get_log_path
    setup_logging = utils_mod.setup_logging

setup_logging()

if __name__ == '__main__':
    def log_tkinter_exception(type, value, tb):
        import traceback
        logging.error('Uncaught exception:', exc_info=(type, value, tb))
        sys.__excepthook__(type, value, tb)
    sys.excepthook = log_tkinter_exception
    try:
        app = AppConfigurator()
        app.mainloop()
    except Exception as e:
        logging.error(f"Fatal error in mainloop: {e}", exc_info=True)
