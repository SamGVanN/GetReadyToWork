"""
GUI module for GetReadyToWork application configurator.
Provides a Tkinter-based interface for selecting and managing applications to launch.
"""
import os
import sys
import json
import threading
import subprocess
import importlib
import importlib.util
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging

# Initialisation du logging commun dès le lancement du module
try:
    # Essai import absolu (mode dev, script, ou frozen)
    from src.common.utils import setup_logging
except ImportError:
    try:
        from common.utils import setup_logging
    except ImportError:
        try:
            exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            utils_path = os.path.join(exe_dir, 'common', 'utils.py')
            if not os.path.exists(utils_path):
                utils_path = os.path.join(os.path.dirname(__file__), '..', '..', 'common', 'utils.py')
            spec = importlib.util.spec_from_file_location('common.utils', utils_path)
            utils_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(utils_mod)
            setup_logging = utils_mod.setup_logging
        except (ImportError, AttributeError, FileNotFoundError) as e:
            logging.basicConfig(filename='logs.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')
            logging.error("[FATAL] Impossible d'importer setup_logging: %s", e)
            raise
setup_logging()
logging.info('--- Lancement module GUI.py ---')

# --- Début correctif robustesse et i18n ---
try:
    # Import i18n resources dynamiquement (compatible frozen/script)
    try:
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            i18n_path = os.path.join(exe_dir, 'i18n_resources.py')
            if not os.path.exists(i18n_path):
                config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
                if config_dir not in sys.path:
                    sys.path.insert(0, config_dir)
                i18n_mod = importlib.import_module('i18n_resources')
            else:
                spec = importlib.util.spec_from_file_location('i18n_resources', i18n_path)
                i18n_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(i18n_mod)
        else:
            try:
                i18n_mod = importlib.import_module('config.i18n_resources')
            except ImportError:
                config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
                if config_dir not in sys.path:
                    sys.path.insert(0, config_dir)
                i18n_mod = importlib.import_module('i18n_resources')
        messages = i18n_mod.messages
        messages_fr = i18n_mod.messages_fr
    except (ImportError, AttributeError) as e:
        print("[FATAL] Could not import i18n_resources: %s" % e)
        messages = {"title": "Application selection"}
        messages_fr = {"title": "Paramétrage des applications à lancer"}
    import locale
    lang = locale.getdefaultlocale()[0]
    if lang and lang.startswith('fr'):
        _ = messages_fr
    else:
        _ = messages
except (ImportError, AttributeError):
    _ = {"title": "Application selection"}

# --- Fin correctif robustesse et i18n ---

# --- Définition des chemins de config robustes ---
try:
    from src.common.config_manager import get_config_file, get_scan_paths_file
except ImportError:
    try:
        from common.config_manager import get_config_file, get_scan_paths_file
    except ImportError:
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        cm_path = os.path.join(exe_dir, 'common', 'config_manager.py')
        if not os.path.exists(cm_path):
            cm_path = os.path.join(os.path.dirname(__file__), '..', '..', 'common', 'config_manager.py')
        spec = importlib.util.spec_from_file_location('common.config_manager', cm_path)
        cm_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cm_mod)
        get_config_file = cm_mod.get_config_file
        get_scan_paths_file = cm_mod.get_scan_paths_file
CONFIG_FILE = get_config_file()
SCAN_PATHS_USER_FILE = get_scan_paths_file()


def list_installed_apps_all_os():
    """
    List installed applications for all supported operating systems.
    Returns a sorted list of application paths.
    """
    apps = []
    if sys.platform.startswith('win'):
        try:
            import winapps
            for app in winapps.list_installed():
                if app.install_location and os.path.isdir(app.install_location):
                    exe = app.install_location
                    found = False
                    for f in os.listdir(exe):
                        if f.lower().endswith('.exe'):
                            apps.append(os.path.join(exe, f))
                            found = True
                    if not found:
                        apps.append(exe)
        except ImportError as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror(
                _["error_winapps"] if "error_winapps" in _ else "Module manquant",
                _["error_winapps"] if "error_winapps" in _ else (
                    "Le module Python 'winapps' est requis pour d\u00e9tecter les applications install\u00e9es sur Windows.\n\nVeuillez l'installer avec :\npip install winapps"
                )
            )
            return []
    elif sys.platform.startswith('darwin'):
        app_dirs = ['/Applications', os.path.expanduser('~/Applications')]
        for app_dir in app_dirs:
            if os.path.isdir(app_dir):
                for f in os.listdir(app_dir):
                    if f.endswith('.app'):
                        apps.append(os.path.join(app_dir, f))
        try:
            output = subprocess.check_output(['brew', 'list', '--cask'], universal_newlines=True)
            for line in output.splitlines():
                apps.append(line.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    else:
        desktop_dirs = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
        for ddir in desktop_dirs:
            if os.path.isdir(ddir):
                for f in os.listdir(ddir):
                    if f.endswith('.desktop'):
                        apps.append(os.path.join(ddir, f))
        try:
            output = subprocess.check_output(['dpkg-query', '-W', '-f=${Package}\n'], universal_newlines=True)
            for line in output.splitlines():
                apps.append(line.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    apps = [str(a) for a in apps]
    return sorted(set(apps))


class AppConfigurator(tk.Tk):
    """
    Main application configurator window for selecting and managing applications to launch.
    """
    def __init__(self):
        """Initialize the AppConfigurator window and widgets."""
        super().__init__()
        self.title(_["title"] if "title" in _ else "GetReadyToWork - Param\u00e9trage")
        self.geometry('900x500')
        self.resizable(False, False)
        self.configure(bg="#23272e")
        self.available_apps = self.find_installed_apps()
        self.selected_apps = self.load_selected_apps()
        self.filtered_apps = self.available_apps.copy()
        self.icons_cache = {}
        self.tooltip = None
        self.lb_available = None
        self.lb_selected = None
        self.vsb_available = None
        self.vsb_selected = None
        self.create_widgets()

    def _get_default_scan_paths(self):
        """
        Robustly load the default scan paths for the current OS, compatible with both dev and frozen modes.
        """
        scan_filename = None
        if sys.platform.startswith('win'):
            scan_filename = 'scan_paths_windows.py'
        elif sys.platform.startswith('darwin'):
            scan_filename = 'scan_paths_mac.py'
        else:
            scan_filename = 'scan_paths_linux.py'
        try:
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                scan_path = os.path.join(exe_dir, scan_filename)
                if not os.path.exists(scan_path):
                    scan_path = os.path.join(getattr(sys, '_MEIPASS', exe_dir), scan_filename)
                if not os.path.exists(scan_path):
                    scan_path = os.path.join(exe_dir, 'config', scan_filename)
            else:
                scan_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', scan_filename))
            spec = importlib.util.spec_from_file_location('scan_paths', scan_path)
            scan_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scan_mod)
            return list(scan_mod.SCAN_PATHS)
        except (ImportError, AttributeError, FileNotFoundError) as e:
            logging.error("Error loading default scan paths (%s): %s", scan_filename, e)
            return []

    def get_scan_paths(self):
        """
        Load scan paths from user config file, or fallback to default scan paths for the OS.
        """
        if os.path.exists(SCAN_PATHS_USER_FILE):
            try:
                with open(SCAN_PATHS_USER_FILE, 'r', encoding='utf-8') as f:
                    paths = json.load(f)
                    if paths:
                        return paths
            except (OSError, json.JSONDecodeError) as e:
                logging.error("Error loading user scan paths: %s", e)
        return self._get_default_scan_paths()

    def save_scan_paths(self, paths):
        """
        Save scan paths to the user config file.
        """
        try:
            os.makedirs(os.path.dirname(SCAN_PATHS_USER_FILE), exist_ok=True)
            with open(SCAN_PATHS_USER_FILE, 'w', encoding='utf-8') as f:
                json.dump(paths, f, indent=2)
        except OSError as e:
            logging.error("Error saving user scan paths: %s", e)

    def find_installed_apps(self):
        """
        Find installed applications by scanning configured paths.
        Returns a sorted list of application paths.
        """
        apps = []
        scan_paths = self.get_scan_paths()
        for root_path in scan_paths:
            if root_path and os.path.exists(root_path):
                for dirpath, dirnames, filenames in os.walk(root_path):
                    if sys.platform.startswith('win'):
                        for f in filenames:
                            if f.lower().endswith('.exe'):
                                apps.append(os.path.join(dirpath, f))
                    elif sys.platform.startswith('darwin'):
                        for d_name in dirnames:
                            if d_name.lower().endswith('.app'):
                                apps.append(os.path.join(dirpath, d_name))
                                dirnames.remove(d_name)
                    else:
                        for f in filenames:
                            file_path = os.path.join(dirpath, f)
                            if os.access(file_path, os.X_OK) and not os.path.isdir(file_path):
                                apps.append(file_path)
        def disk_key(path):
            path_lower = path.lower()
            basename_lower = os.path.basename(path_lower)
            if sys.platform.startswith('win'):
                drive = os.path.splitdrive(path_lower)[0].upper()
                return (drive, basename_lower)
            else:
                dirname_lower = os.path.dirname(path_lower)
                return (dirname_lower, basename_lower)
        return sorted(list(set(apps)), key=disk_key)

    def load_selected_apps(self):
        """
        Load selected applications from the config file.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logging.error("Error loading config: %s", e)
        return []

    def save_selected_apps(self):
        """
        Save selected applications to the config file.
        """
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.selected_apps, f, indent=2)
        except OSError as e:
            logging.error("Error saving config: %s", e)
            messagebox.showerror(_["save"] if "save" in _ else "Sauvegarde", _["error_save_config"] if "error_save_config" in _ else str(e))

    def create_widgets(self):
        """
        Create and layout all widgets for the main window.
        """
        # Style moderne
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background="#23272e")
        style.configure('TLabel', background="#23272e", foreground="#e1e1e6", font=("Segoe UI", 11))
        style.configure('TButton', background="#2c313a", foreground="#e1e1e6", font=("Segoe UI", 10), borderwidth=0)
        style.map('TButton', background=[('active', '#3a3f4b')])
        style.configure('Treeview', background="#23272e", fieldbackground="#23272e", foreground="#e1e1e6", font=("Segoe UI", 10), rowheight=28, borderwidth=0)
        style.configure('Treeview.Heading', background="#23272e", foreground="#e1e1e6", font=("Segoe UI", 11, "bold"))
        style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure('TEntry', fieldbackground="#2c313a", foreground="#e1e1e6", borderwidth=0)
        style.configure('Green.TButton', background="#3dbd5d", foreground="#ffffff", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map('Green.TButton', background=[('active', '#2e8c44')])

        main = ttk.Frame(self)
        main.grid(row=0, column=0, sticky='nsew', padx=24, pady=18)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)

        # --- TITRES AU DESSUS DES ENCADRÉS ---
        available_label = ttk.Label(main, text=_['available'] if 'available' in _ else 'Applications disponibles', font=("Segoe UI", 11, "bold"), background="#23272e", foreground="#eb8f34")
        available_label.grid(row=0, column=0, sticky='w', padx=(0, 20), pady=(0, 2))
        selected_label = ttk.Label(main, text=_['to_launch'] if 'to_launch' in _ else 'Applications à lancer', font=("Segoe UI", 11, "bold"), background="#23272e", foreground="#3dbd5d")
        selected_label.grid(row=0, column=2, sticky='w', padx=(20, 0), pady=(0, 2))

        # Cadres avec contours colorés
        self.frame_available = tk.Frame(main, bg="#23272e", highlightbackground="#eb8f34", highlightcolor="#eb8f34", highlightthickness=2, bd=0)
        self.frame_selected = tk.Frame(main, bg="#23272e", highlightbackground="#3dbd5d", highlightcolor="#3dbd5d", highlightthickness=2, bd=0)
        self.frame_available.grid(row=1, column=0, sticky='nsew', padx=(0, 20), pady=(0,0))
        self.frame_selected.grid(row=1, column=2, sticky='nsew', padx=(20, 0), pady=(0,0))
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(2, weight=1)

        # --- Zone de recherche dans la colonne orange ---
        search_frame = ttk.Frame(self.frame_available)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(8, 8), padx=8)
        search_label = ttk.Label(search_frame, text=_['search'] if 'search' in _ else 'Rechercher')
        search_label.pack(side='left', padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=32)
        search_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)

        # --- Liste applis + scrollbar ---
        self.lb_available = ttk.Treeview(self.frame_available, columns=('name',), show='tree', selectmode='extended')
        self.vsb_available = ttk.Scrollbar(self.frame_available, orient="vertical", command=self.lb_available.yview)
        self.lb_available.configure(yscrollcommand=self.vsb_available.set)
        self.frame_available.rowconfigure(0, weight=0)  # zone de recherche
        self.frame_available.rowconfigure(1, weight=1)  # liste applis
        self.frame_available.columnconfigure(0, weight=1)
        self.lb_available.grid(row=1, column=0, sticky='nsew', padx=(8,0), pady=(0,8))
        self.vsb_available.grid(row=1, column=1, sticky='ns', pady=(0,8), padx=(0,8))

        # Treeview + scrollbar pour sélectionnées (utilise grid aussi pour cohérence)
        self.lb_selected = ttk.Treeview(self.frame_selected, columns=('name',), show='tree', selectmode='extended')
        self.vsb_selected = ttk.Scrollbar(self.frame_selected, orient="vertical", command=self.lb_selected.yview)
        self.lb_selected.configure(yscrollcommand=self.vsb_selected.set)
        self.frame_selected.rowconfigure(0, weight=1)
        self.frame_selected.columnconfigure(0, weight=1)
        self.lb_selected.grid(row=0, column=0, sticky='nsew')
        self.vsb_selected.grid(row=0, column=1, sticky='ns')

        # Bindings scroll souris propres à chaque colonne
        self.lb_available.bind('<Enter>', lambda e: self._bind_mousewheel(self.lb_available))
        self.lb_available.bind('<Leave>', lambda e: self._unbind_mousewheel(self.lb_available))
        self.lb_selected.bind('<Enter>', lambda e: self._bind_mousewheel(self.lb_selected))
        self.lb_selected.bind('<Leave>', lambda e: self._unbind_mousewheel(self.lb_selected))

        # --- Colonne centrale : flèches + boutons d'action verticaux ---
        btns = ttk.Frame(main)
        btns.grid(row=1, column=1, sticky='ns', pady=(0,0))
        # Flèches en haut
        ttk.Button(btns, text='→', command=self.add_app, width=4).pack(pady=(10, 5))
        ttk.Button(btns, text='←', command=self.remove_app, width=4).pack(pady=(0, 20))
        # Boutons d'action verticaux
        edit_btn = ttk.Button(btns, text="Modifier les dossiers à scanner", command=self.edit_scan_paths, width=28)
        edit_btn.pack(pady=(0, 8), fill='x')
        manual_btn = ttk.Button(btns, text=_['manual_select'] if 'manual_select' in _ else "Choisir manuellement une application", command=self.open_manual_app_selector, width=28)
        manual_btn.pack(pady=(0, 8), fill='x')
        save_btn = ttk.Button(btns, text=_['save'] if 'save' in _ else 'Sauvegarder', command=self.save_selected_apps, style='Green.TButton', width=22)
        save_btn.pack(pady=(0, 8), fill='x')
        save_close_btn = ttk.Button(btns, text="Sauvegarder et fermer", command=self._save_and_close, width=22)
        save_close_btn.pack(pady=(0, 0), fill='x')

        # Frame pour le bouton Sauvegarder en bas
        save_frame = ttk.Frame(self)
        save_frame.grid(row=1, column=0, sticky='ew', padx=24, pady=(0, 18))
        self.rowconfigure(1, weight=0)

        # Bindings
        self.lb_available.bind('<Double-Button-1>', lambda e: self.add_app())
        self.lb_selected.bind('<Double-Button-1>', lambda e: self.remove_app())
        self.lb_available.bind('<Motion>', self.on_treeview_hover)
        self.lb_selected.bind('<Motion>', self.on_treeview_hover)
        self.bind('<Button-1>', self.hide_tooltip)

        self.refresh_lists()

    def show_loader(self):
        """
        Display a loading label overlay in the available apps frame.
        """
        if hasattr(self, 'loader_label') and self.loader_label is not None:
            return
        self.loader_label = tk.Label(self.frame_available, text="⏳ " + (_['loading'] if 'loading' in _ else 'Chargement...'),
                                     bg="#23272e", fg="#eb8f34", font=("Segoe UI", 13, "bold"))
        self.loader_label.place(relx=0.5, rely=0.5, anchor='center')
        self.update_idletasks()

    def hide_loader(self):
        """
        Remove the loading label overlay if present.
        """
        if hasattr(self, 'loader_label') and self.loader_label is not None:
            self.loader_label.destroy()
            self.loader_label = None

    def refresh_lists(self):
        """
        Refresh the available and selected apps lists in the UI.
        """
        # Vide le contenu des Treeview sans les détruire
        for tree in (self.lb_available, self.lb_selected):
            tree.delete(*tree.get_children())
        # Platform-aware sorting key (defined in find_installed_apps, but conceptually used here too for sorting before display)
        def get_group_key(path):
            if sys.platform.startswith('win'):
                return os.path.splitdrive(path)[0].upper() or "(C:)" # Default if no drive
            else: # Group by parent directory for macOS/Linux
                return os.path.dirname(path) or "/" # Default if root

        # Liste de gauche (dispo) : treelist par groupe (disque ou dossier parent)
        groups_available = {}
        # Use the same disk_key from find_installed_apps for sorting to ensure consistency
        # The disk_key function sorts by (group, name)
        for app_path in self.filtered_apps: # self.filtered_apps is already sorted by disk_key
            group_name = get_group_key(app_path)
            if group_name not in groups_available:
                groups_available[group_name] = []
            groups_available[group_name].append({'name': os.path.basename(app_path), 'path': app_path})

        for group_name in sorted(groups_available.keys()):
            parent = self.lb_available.insert('', 'end', text=group_name, open=True)
            for child_app in sorted(groups_available[group_name], key=lambda x: x['name'].lower()):
                self.lb_available.insert(parent, 'end', text=child_app['name'], tags=(child_app['path'],))

        # Liste de droite (choisies) : treelist par groupe
        groups_selected = {}
        # self.selected_apps should also be sorted before display grouping
        # We can sort it using the disk_key from find_installed_apps if it's not already
        # For simplicity, assume self.selected_apps might not be pre-sorted like self.filtered_apps
        # However, the disk_key in find_installed_apps is not directly accessible here.
        # Re-define a simple sort key for selected_apps for now or ensure it's sorted upon modification.
        
        # Let's re-use get_group_key and sort selected_apps locally for grouping
        # Create a temporary sorted list for selected apps for display grouping
        temp_sorted_selected_apps = sorted(self.selected_apps, key=lambda app_path: (get_group_key(app_path), os.path.basename(app_path).lower()))

        for app_path in temp_sorted_selected_apps:
            group_name_sel = get_group_key(app_path)
            if group_name_sel not in groups_selected:
                groups_selected[group_name_sel] = []
            groups_selected[group_name_sel].append({'name': os.path.basename(app_path), 'path': app_path})
            
        for group_name_sel in sorted(groups_selected.keys()):
            parent = self.lb_selected.insert('', 'end', text=group_name_sel, open=True)
            for child_app in sorted(groups_selected[group_name_sel], key=lambda x: x['name'].lower()):
                self.lb_selected.insert(parent, 'end', text=child_app['name'], tags=(child_app['path'],))
        # Rebinds
        self.lb_available.bind('<Double-Button-1>', lambda e: self.add_app())
        self.lb_available.bind('<Motion>', self.on_treeview_hover)
        self.lb_selected.bind('<Double-Button-1>', lambda e: self.remove_app())
        self.lb_selected.bind('<Motion>', self.on_treeview_hover)

    def on_search(self, *args):
        """
        Filter available apps based on the search query.
        """
        query = self.search_var.get().lower()
        self.filtered_apps = [a for a in self.available_apps if query in os.path.basename(a).lower()]
        self.refresh_lists()

    def add_app(self):
        """
        Add selected app(s) from available list to selected list.
        """
        try:
            selection = self.lb_available.selection()
            for item in selection:
                app = None
                for tag in self.lb_available.item(item, 'tags'):
                    if os.path.isabs(tag):
                        app = tag
                if app and app not in self.selected_apps:
                    self.selected_apps.append(app)
            self.refresh_lists()
        except (tk.TclError, IndexError) as e:
            logging.error("Error adding app: %s", e)

    def remove_app(self):
        """
        Remove selected app(s) from the selected list.
        """
        try:
            selection = self.lb_selected.selection()
            for item in selection:
                app = None
                for tag in self.lb_selected.item(item, 'tags'):
                    if os.path.isabs(tag):
                        app = tag
                if app and app in self.selected_apps:
                    self.selected_apps.remove(app)
            self.refresh_lists()
        except (tk.TclError, IndexError) as e:
            logging.error("Error removing app: %s", e)

    def on_treeview_hover(self, event):
        """
        Show tooltip with app path when hovering over a treeview item.
        """
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            app_path = None
            for tag in tree.item(item, 'tags'):
                if os.path.isabs(tag):
                    app_path = tag
            if app_path:
                self.show_tooltip(tree, event.x_root, event.y_root, app_path)
        else:
            self.hide_tooltip()

    def show_tooltip(self, widget, x, y, text):
        """
        Display a tooltip with the given text at the specified position.
        """
        self.hide_tooltip()
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f'+{x+20}+{y+10}')
        label = ttk.Label(self.tooltip, text=text, background='#f5f5f5', foreground='#23272e', borderwidth=1, relief='solid', font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=2)

    def hide_tooltip(self, event=None):
        """
        Hide the tooltip if it is visible.
        """
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def edit_scan_paths(self):
        """
        Open a window to edit the scan paths for application discovery.
        """
        # Si la fenêtre existe déjà, la mettre en avant
        if hasattr(self, 'scan_path_window') and self.scan_path_window is not None and self.scan_path_window.winfo_exists():
            self.scan_path_window.lift()
            self.scan_path_window.focus_force()
            return
        win = tk.Toplevel(self)
        self.scan_path_window = win
        win.title(_["scan_paths_window_title"] if "scan_paths_window_title" in _ else "Chemins à scanner")
        win.geometry("600x400")
        win.configure(bg="#23272e")
        def on_close():
            self.scan_path_window = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)
        paths = self.get_scan_paths()
        var_list = []
        entry_list = []
        frame = ttk.Frame(win)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        def refresh_entries():
            for widget in frame.winfo_children():
                widget.destroy()
            entry_list.clear()
            for i, var in enumerate(var_list):
                entry = ttk.Entry(frame, textvariable=var, width=70)
                entry.grid(row=i, column=0, sticky='ew', pady=3)
                entry_list.append(entry)
                # Bouton supprimer
                btn = ttk.Button(frame, text=_["remove_path"] if "remove_path" in _ else "✕", width=2, command=lambda idx=i: remove_path(idx))
                btn.grid(row=i, column=1, padx=(5,0))
        def add_path():
            # Ouvre un explorateur pour choisir un dossier
            folder = filedialog.askdirectory(title=_["scan_paths_add_title"] if "scan_paths_add_title" in _ else "Choisir un dossier à scanner")
            if folder:
                var = tk.StringVar(value=folder)
                var_list.append(var)
                refresh_entries()
        def remove_path(idx):
            del var_list[idx]
            refresh_entries()
        def reset_to_default():
            # Recharge les chemins par défaut selon l'OS, robustement (dev/frozen)
            try:
                SCAN_PATHS = self._get_default_scan_paths()
                var_list.clear()
                for path in SCAN_PATHS:
                    var = tk.StringVar(value=path)
                    var_list.append(var)
                refresh_entries()
            except Exception as e:
                logging.error(f"Error resetting scan paths to default: {e}")
        # Initialisation
        for path in paths:
            var = tk.StringVar(value=path)
            var_list.append(var)
        refresh_entries()
        ttk.Button(win, text=_["add_path"] if "add_path" in _ else "Ajouter un chemin", command=add_path, width=22).pack(pady=(0, 10))
        ttk.Button(win, text=_["reset_to_default"] if "reset_to_default" in _ else "Reset to default", command=reset_to_default, width=22).pack(pady=(0, 10))
        def save_and_close():
            new_paths = [v.get() for v in var_list if v.get().strip()]
            self.save_scan_paths(new_paths)
            self.scan_path_window = None
            win.destroy()
            # Affiche le loader sans détruire les widgets existants
            self.show_loader()
            # Recherche des apps dans un thread pour ne pas bloquer l'UI
            def update_apps():
                self.available_apps = self.find_installed_apps()
                self.filtered_apps = self.available_apps.copy()
                self.after(0, lambda: (self.hide_loader(), self.refresh_lists()))
            threading.Thread(target=update_apps, daemon=True).start()
        ttk.Button(win, text=_["save_paths"] if "save_paths" in _ else "Sauvegarder", command=save_and_close, style='Green.TButton', width=22).pack(pady=10)

    def open_manual_app_selector(self):
        """
        Open a window to manually select installed applications from all detected apps.
        """
        if hasattr(self, 'manual_app_window') and self.manual_app_window is not None and self.manual_app_window.winfo_exists():
            self.manual_app_window.lift()
            self.manual_app_window.focus_force()
            return
        win = tk.Toplevel(self)
        self.manual_app_window = win
        win.title(_["manual_select_title"] if "manual_select_title" in _ else "Sélection manuelle d'applications")
        win.geometry("700x700")
        win.configure(bg="#23272e")
        def on_close():
            self.manual_app_window = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", on_close)
        # Affiche un loader pendant la détection
        loader = ttk.Label(win, text=_["loading"] if "loading" in _ else 'Chargement...', background="#23272e", foreground="#eb8f34", font=("Segoe UI", 12, "bold"))
        loader.pack(expand=True, fill='both')
        import threading
        def load_and_show():
            all_apps = list_installed_apps_all_os()
            # Trie par disque ou dossier parent
            from collections import defaultdict
            apps_by_group = defaultdict(list) # Renamed for clarity and consistency
            for app_path in all_apps:
                if sys.platform.startswith('win'):
                    group_key = os.path.splitdrive(app_path)[0].upper() or "(C:)"
                else: # Group by parent directory for macOS/Linux
                    group_key = os.path.dirname(app_path) or "/"
                apps_by_group[group_key].append(app_path)

            def show_ui():
                loader.destroy()
                # Scrollable frame
                canvas = tk.Canvas(win, bg="#23272e", highlightthickness=0)
                frame = ttk.Frame(canvas)
                vsb = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=vsb.set)
                vsb.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                canvas.create_window((0,0), window=frame, anchor='nw')
                def on_frame_configure(event):
                    canvas.configure(scrollregion=canvas.bbox("all"))
                frame.bind("<Configure>", on_frame_configure)
                # Cases à cocher
                check_vars = {}
                row = 0
                for group_key in sorted(apps_by_group.keys()):
                    group_label = ttk.Label(frame, text=group_key, background="#23272e", foreground="#eb8f34", font=("Segoe UI", 11, "bold"))
                    group_label.grid(row=row, column=0, sticky='w', pady=(10,2))
                    row += 1
                    # Sort apps within each group by name
                    for app_path in sorted(apps_by_group[group_key], key=lambda p: os.path.basename(p).lower()):
                        var = tk.BooleanVar(value=app_path in self.selected_apps)
                        check_vars[app_path] = var # Use app_path as key
                        cb = ttk.Checkbutton(frame, text=os.path.basename(app_path), variable=var, style='TCheckbutton')
                        cb.grid(row=row, column=0, sticky='w', padx=20)
                        row += 1
                def add_selected():
                    for app, var in check_vars.items():
                        if var.get() and app not in self.selected_apps:
                            self.selected_apps.append(app)
                    self.refresh_lists()
                    self.manual_app_window = None
                    win.destroy()
                ttk.Button(win, text=_["manual_select_add"] if "manual_select_add" in _ else "Ajouter à la sélection", command=add_selected, style='Green.TButton').pack(pady=10)
            self.after(0, show_ui)
        threading.Thread(target=load_and_show, daemon=True).start()

    def _on_mousewheel(self, event, tree):
        """
        Handle mouse wheel scrolling for the given treeview.
        """
        # Compatible Windows/Mac/Linux
        if event.num == 5 or event.delta == -120:
            tree.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            tree.yview_scroll(-1, "units")
        return "break"

    def _bind_mousewheel(self, tree):
        """
        Bind mouse wheel events to the given treeview.
        """
        tree.bind_all('<MouseWheel>', lambda e: self._on_mousewheel(e, tree))
        tree.bind_all('<Button-4>', lambda e: self._on_mousewheel(e, tree))
        tree.bind_all('<Button-5>', lambda e: self._on_mousewheel(e, tree))

    def _unbind_mousewheel(self, tree):
        """
        Unbind mouse wheel events from the given treeview.
        """
        tree.unbind_all('<MouseWheel>')
        tree.unbind_all('<Button-4>')
        tree.unbind_all('<Button-5>')

    def _save_and_close(self):
        """
        Save selected apps and close the configurator window.
        """
        self.save_selected_apps()
        self.destroy()
