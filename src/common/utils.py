import os
import sys
import json
import locale
import subprocess
import logging

def get_log_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'logs.log')

def setup_logging():
    logging.basicConfig(
        filename=get_log_path(),
        encoding='utf-8',
        level=logging.DEBUG,
        force=True,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.debug('Logging initialized at script start.')

def load_apps_to_execute(config_path):
    """Load the list of apps to execute from a config file."""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
    return []

def launch_app(app_path):
    """Launch an application cross-platform."""
    try:
        if sys.platform.startswith('win'):
            os.startfile(app_path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', app_path])
        else:
            subprocess.Popen(['xdg-open', app_path])
    except Exception as e:
        logging.error(f"Failed launching app: {app_path} | {e}")

def get_i18n_messages(i18n_mod=None):
    """Return the appropriate i18n messages dict for the current locale."""
    lang = locale.getdefaultlocale()[0]
    if i18n_mod is not None:
        messages = getattr(i18n_mod, 'messages', {})
        messages_fr = getattr(i18n_mod, 'messages_fr', {})
        if lang and lang.startswith('fr'):
            return messages_fr
        else:
            return messages
    return {}
