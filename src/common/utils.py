import os
import sys
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
