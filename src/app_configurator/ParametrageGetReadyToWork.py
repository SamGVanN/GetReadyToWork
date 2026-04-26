import sys
import os
import logging
import locale

# Always use absolute import for GUI
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app_configurator.GUI import AppConfigurator

if __name__ == "__main__":
    app = AppConfigurator()
    app.mainloop()
