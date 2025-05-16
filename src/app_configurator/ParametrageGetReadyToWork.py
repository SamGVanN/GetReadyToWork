import os
import sys
import logging
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import locale
import subprocess
import threading
import importlib
# Always write logs to a file in the same directory as the executable (build or src)
def get_log_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'logs.log')
logging.basicConfig(filename=get_log_path(), encoding='utf-8', level=logging.DEBUG, force=True)
logging.debug('Logging initialized at script start.')

try:
    logging.debug('Starting main import and initialization.')
    if getattr(sys, 'frozen', False):
        # Running as exe: add build folder to sys.path
        sys.path.insert(0, os.path.dirname(sys.executable))
        # Ajoute le dossier 'lib' du build au sys.path pour les modules comme winapps
        lib_dir = os.path.join(os.path.dirname(sys.executable), 'lib')
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)
    else:
        # Running as script: add src/config to sys.path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'config')))
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
    try:
        from config.i18n_resources import messages, messages_fr
    except ImportError:
        from i18n_resources import messages, messages_fr
    logging.debug('Imports and i18n loaded.')
    lang = locale.getdefaultlocale()[0]
    if lang and lang.startswith('fr'):
        _ = messages_fr
    else:
        _ = messages
    logging.debug(f'Locale detected: {lang}')
    # --- Détermination robuste des chemins de fichiers runtime/config ---
    if getattr(sys, 'frozen', False):
        # En mode frozen, tout est dans le dossier du binaire
        base_dir = os.path.dirname(sys.executable)
        runtime_dir = base_dir
        config_dir = base_dir
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        runtime_dir = os.path.abspath(os.path.join(base_dir, '..', '..', 'runtime'))
        config_dir = os.path.abspath(os.path.join(base_dir, '..', 'config'))
    # S'assure que les dossiers existent si besoin d'écriture
    os.makedirs(runtime_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)
    CONFIG_FILE = os.path.join(runtime_dir, 'apps_to_launch.json')
    SCAN_PATHS_USER_FILE = os.path.join(config_dir, 'scan_paths_user.json')

    def list_installed_apps_all_os():
        apps = []
        if sys.platform.startswith('win'):
            try:
                import winapps
                logging.debug('winapps import OK')
                for app in winapps.list_installed():
                    if app.install_location and os.path.isdir(app.install_location):
                        exe = app.install_location
                        # Cherche un .exe principal
                        found = False
                        for f in os.listdir(exe):
                            if f.lower().endswith('.exe'):
                                apps.append(os.path.join(exe, f))
                                found = True
                        if not found:
                            # Ajoute le dossier si pas d'exe trouvé
                            apps.append(exe)
            except ImportError as e:
                logging.error(f"winapps import failed: {e}")
                # Affiche un message d'erreur à l'utilisateur si winapps n'est pas installé
                import tkinter.messagebox
                tkinter.messagebox.showerror(
                    _["error_winapps"] if "error_winapps" in _ else "Module manquant",
                    _["error_winapps"] if "error_winapps" in _ else "Le module Python 'winapps' est requis pour détecter les applications installées sur Windows.\n\nVeuillez l'installer avec :\npip install winapps"
                )
                return []
        elif sys.platform.startswith('darwin'):
            # macOS: /Applications et ~/Applications
            app_dirs = ['/Applications', os.path.expanduser('~/Applications')]
            for app_dir in app_dirs:
                if os.path.isdir(app_dir):
                    for f in os.listdir(app_dir):
                        if f.endswith('.app'):
                            apps.append(os.path.join(app_dir, f))
            # Homebrew casks
            try:
                output = subprocess.check_output(['brew', 'list', '--cask'], universal_newlines=True)
                for line in output.splitlines():
                    apps.append(line.strip())
            except Exception:
                pass
        else:
            # Linux: .desktop files
            desktop_dirs = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
            for ddir in desktop_dirs:
                if os.path.isdir(ddir):
                    for f in os.listdir(ddir):
                        if f.endswith('.desktop'):
                            apps.append(os.path.join(ddir, f))
            # Paquets installés (Debian/Ubuntu)
            try:
                output = subprocess.check_output(['dpkg-query', '-W', '-f=${Package}\n'], universal_newlines=True)
                for line in output.splitlines():
                    apps.append(line.strip())
            except Exception:
                pass
        apps = [str(a) for a in apps]
        return sorted(set(apps))

    class AppConfigurator(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title(_["title"] if "title" in _ else "GetReadyToWork - Paramétrage")
            self.geometry('900x500')
            self.resizable(False, False)
            self.configure(bg="#23272e")
            self.available_apps = self.find_installed_apps()
            self.selected_apps = self.load_selected_apps()
            self.filtered_apps = self.available_apps.copy()
            self.icons_cache = {}
            self.tooltip = None
            self.create_widgets()

        def get_scan_paths(self):
            # Charge les paths depuis un fichier de config utilisateur, sinon charge les valeurs par défaut selon l'OS
            if os.path.exists(SCAN_PATHS_USER_FILE):
                try:
                    with open(SCAN_PATHS_USER_FILE, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logging.error(f"Error loading user scan paths: {e}")
            # Fallback: charge les chemins par défaut selon l'OS
            try:
                if sys.platform.startswith('win'):
                    module_names = ['config.scan_paths_windows', 'scan_paths_windows']
                elif sys.platform.startswith('darwin'):
                    module_names = ['config.scan_paths_mac', 'scan_paths_mac']
                else:
                    module_names = ['config.scan_paths_linux', 'scan_paths_linux']
                for mod_name in module_names:
                    try:
                        mod = importlib.import_module(mod_name)
                        return mod.SCAN_PATHS
                    except ImportError:
                        continue
                raise ImportError(f"Could not import scan paths module for OS: {sys.platform}")
            except Exception as e:
                logging.error(f"Error loading default scan paths: {e}")
                return []

        def save_scan_paths(self, paths):
            try:
                os.makedirs(os.path.dirname(SCAN_PATHS_USER_FILE), exist_ok=True)
                with open(SCAN_PATHS_USER_FILE, 'w', encoding='utf-8') as f:
                    json.dump(paths, f, indent=2)
            except Exception as e:
                logging.error(f"Error saving user scan paths: {e}")

        def find_installed_apps(self):
            apps = []
            scan_paths = self.get_scan_paths()
            for root in scan_paths:
                if root and os.path.exists(root):
                    for dirpath, dirnames, filenames in os.walk(root):
                        for f in filenames:
                            if f.lower().endswith('.exe'):
                                apps.append(os.path.join(dirpath, f))
            # Trie par disque puis nom
            def disk_key(path):
                drive = os.path.splitdrive(path)[0].upper()
                return (drive, os.path.basename(path).lower())
            return sorted(set(apps), key=disk_key)

        def load_selected_apps(self):
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logging.error(f"Error loading config: {e}")
            return []

        def save_selected_apps(self):
            try:
                os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.selected_apps, f, indent=2)
            except Exception as e:
                logging.error(f"Error saving config: {e}")
                messagebox.showerror(_["save"] if "save" in _ else "Sauvegarde", _["error_save_config"] if "error_save_config" in _ else str(e))

        def create_widgets(self):
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
            main.pack(expand=True, fill='both', padx=30, pady=30)

            # Champ de recherche et bouton sur la même ligne
            search_frame = ttk.Frame(main)
            search_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 8))
            search_label = ttk.Label(search_frame, text=_['search'] if 'search' in _ else 'Rechercher')
            search_label.pack(side='left', padx=(0, 10))
            self.search_var = tk.StringVar()
            self.search_var.trace_add('write', self.on_search)
            search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
            search_entry.pack(side='left', padx=(0, 10))
            edit_btn = ttk.Button(search_frame, text="Modifier les dossiers à scanner", command=self.edit_scan_paths)
            edit_btn.pack(side='right')
            main.columnconfigure(0, weight=1)
            main.columnconfigure(1, weight=0)
            main.columnconfigure(2, weight=0)

            # Cadres avec contours colorés
            self.frame_available = tk.Frame(main, bg="#23272e", highlightbackground="#eb8f34", highlightcolor="#eb8f34", highlightthickness=2, bd=0)
            self.frame_selected = tk.Frame(main, bg="#23272e", highlightbackground="#3dbd5d", highlightcolor="#3dbd5d", highlightthickness=2, bd=0)
            self.frame_available.grid(row=1, column=0, sticky='nsew', padx=(0, 20))
            self.frame_selected.grid(row=1, column=2, sticky='nsew', padx=(20, 0))
            main.columnconfigure(0, weight=1)
            main.columnconfigure(2, weight=1)

            # Treeview avec treelist par disque
            self.lb_available = ttk.Treeview(self.frame_available, columns=('name',), show='tree', height=16, selectmode='extended')
            self.lb_selected = ttk.Treeview(self.frame_selected, columns=('name',), show='tree', height=16, selectmode='extended')
            self.lb_available.pack(expand=True, fill='both', padx=0, pady=0)
            self.lb_selected.pack(expand=True, fill='both', padx=0, pady=0)

            # Entêtes
            self.lb_available.heading('#0', text=_['available'] if 'available' in _ else 'Applications disponibles')
            self.lb_selected.heading('#0', text=_['to_launch'] if 'to_launch' in _ else 'À lancer')

            # Boutons
            btns = ttk.Frame(main)
            btns.grid(row=1, column=1, sticky='ns')
            ttk.Button(btns, text='→', command=self.add_app, width=4).pack(pady=10)
            ttk.Button(btns, text='←', command=self.remove_app, width=4).pack(pady=10)
            # Nouveau bouton pour choisir manuellement une application
            manual_btn = ttk.Button(btns, text=_["manual_select"] if "manual_select" in _ else "Choisir manuellement une application", command=self.open_manual_app_selector, width=40)
            manual_btn.pack(pady=10)
            ttk.Button(btns, text=_['save'] if 'save' in _ else 'Sauvegarder', command=self.save_selected_apps, width=12, style='Green.TButton').pack(pady=30)

            # Bindings
            self.lb_available.bind('<Double-Button-1>', lambda e: self.add_app())
            self.lb_selected.bind('<Double-Button-1>', lambda e: self.remove_app())
            self.lb_available.bind('<Motion>', self.on_treeview_hover)
            self.lb_selected.bind('<Motion>', self.on_treeview_hover)
            self.bind('<Button-1>', self.hide_tooltip)

            self.refresh_lists()

        def show_loader(self):
            if hasattr(self, 'loader_label') and self.loader_label is not None:
                return
            self.loader_label = tk.Label(self.frame_available, text="⏳ " + (_['loading'] if 'loading' in _ else 'Chargement...'),
                                         bg="#23272e", fg="#eb8f34", font=("Segoe UI", 13, "bold"))
            self.loader_label.place(relx=0.5, rely=0.5, anchor='center')
            self.update_idletasks()

        def hide_loader(self):
            if hasattr(self, 'loader_label') and self.loader_label is not None:
                self.loader_label.destroy()
                self.loader_label = None

        def refresh_lists(self):
            # Affiche un loader dans la colonne de gauche
            for widget in self.frame_available.winfo_children():
                widget.destroy()
            loader_label = ttk.Label(self.frame_available, text=_['loading'] if 'loading' in _ else 'Chargement...', background="#23272e", foreground="#eb8f34", font=("Segoe UI", 12, "bold"))
            loader_label.pack(expand=True, fill='both')

            def do_refresh():
                # Trie par disque puis nom
                def disk_key(path):
                    drive = os.path.splitdrive(path)[0].upper()
                    return (drive, os.path.basename(path).lower())
                # Liste de gauche (dispo) : treelist par disque
                available_items = []
                drives = {}
                for app in sorted(self.filtered_apps, key=disk_key):
                    drive = os.path.splitdrive(app)[0].upper()
                    if drive not in drives:
                        drives[drive] = {'id': drive, 'children': []}
                    name = os.path.basename(app)
                    drives[drive]['children'].append({'name': name, 'path': app})
                available_items = drives
                # Liste de droite (choisies) : treelist par disque
                drives_sel = {}
                for app in sorted(self.selected_apps, key=disk_key):
                    drive = os.path.splitdrive(app)[0].upper()
                    if drive not in drives_sel:
                        drives_sel[drive] = {'id': drive, 'children': []}
                    name = os.path.basename(app)
                    drives_sel[drive]['children'].append({'name': name, 'path': app})
                selected_items = drives_sel
                def update_ui():
                    # Supprime le loader
                    for widget in self.frame_available.winfo_children():
                        widget.destroy()
                    # Treeview avec treelist par disque
                    self.lb_available = ttk.Treeview(self.frame_available, columns=('name',), show='tree', height=16, selectmode='extended')
                    self.lb_available.pack(expand=True, fill='both', padx=0, pady=0)
                    self.lb_available.heading('#0', text=_['available'] if 'available' in _ else 'Applications disponibles')
                    # Ajoute les apps disponibles
                    for drive, data in available_items.items():
                        parent = self.lb_available.insert('', 'end', text=drive if drive else '(?)', open=True)
                        for child in data['children']:
                            self.lb_available.insert(parent, 'end', text=child['name'], tags=(child['path'],))
                    # Bindings
                    self.lb_available.bind('<Double-Button-1>', lambda e: self.add_app())
                    self.lb_available.bind('<Motion>', self.on_treeview_hover)
                    # Colonne de droite
                    for widget in self.frame_selected.winfo_children():
                        widget.destroy()
                    self.lb_selected = ttk.Treeview(self.frame_selected, columns=('name',), show='tree', height=16, selectmode='extended')
                    self.lb_selected.pack(expand=True, fill='both', padx=0, pady=0)
                    self.lb_selected.heading('#0', text=_['to_launch'] if 'to_launch' in _ else 'À lancer')
                    for drive, data in selected_items.items():
                        parent = self.lb_selected.insert('', 'end', text=drive if drive else '(?)', open=True)
                        for child in data['children']:
                            self.lb_selected.insert(parent, 'end', text=child['name'], tags=(child['path'],))
                    self.lb_selected.bind('<Double-Button-1>', lambda e: self.remove_app())
                    self.lb_selected.bind('<Motion>', self.on_treeview_hover)

                self.after(0, update_ui)

            # Lance le rafraîchissement dans un thread pour ne pas bloquer l'UI
            threading.Thread(target=do_refresh, daemon=True).start()

        def on_search(self, *args):
            query = self.search_var.get().lower()
            self.filtered_apps = [a for a in self.available_apps if query in os.path.basename(a).lower()]
            self.refresh_lists()

        def add_app(self):
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
            except Exception as e:
                logging.error(f"Error adding app: {e}")

        def remove_app(self):
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
            except Exception as e:
                logging.error(f"Error removing app: {e}")

        def on_treeview_hover(self, event):
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
            self.hide_tooltip()
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f'+{x+20}+{y+10}')
            label = ttk.Label(self.tooltip, text=text, background='#f5f5f5', foreground='#23272e', borderwidth=1, relief='solid', font=("Segoe UI", 9))
            label.pack(ipadx=6, ipady=2)

        def hide_tooltip(self, event=None):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

        def edit_scan_paths(self):
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
                # Recharge les chemins par défaut selon l'OS
                try:
                    if sys.platform.startswith('win'):
                        module_names = ['config.scan_paths_windows', 'scan_paths_windows']
                    elif sys.platform.startswith('darwin'):
                        module_names = ['config.scan_paths_mac', 'scan_paths_mac']
                    else:
                        module_names = ['config.scan_paths_linux', 'scan_paths_linux']
                    for mod_name in module_names:
                        try:
                            mod = importlib.import_module(mod_name)
                            SCAN_PATHS = mod.SCAN_PATHS
                            break
                        except ImportError:
                            continue
                    else:
                        raise ImportError(f"Could not import scan paths module for OS: {sys.platform}")
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
            ttk.Button(win, text=_["add_path"] if "add_path" in _ else "Ajouter un chemin", command=add_path).pack(pady=(0, 10))
            ttk.Button(win, text=_["reset_to_default"] if "reset_to_default" in _ else "Reset to default", command=reset_to_default).pack(pady=(0, 10))
            def save_and_close():
                new_paths = [v.get() for v in var_list if v.get().strip()]
                self.save_scan_paths(new_paths)
                self.scan_path_window = None
                win.destroy()
                # Affiche le loader immédiatement
                for widget in self.frame_available.winfo_children():
                    widget.destroy()
                loader_label = ttk.Label(self.frame_available, text=_["loading"] if "loading" in _ else "Chargement...", background="#23272e", foreground="#eb8f34", font=("Segoe UI", 12, "bold"))
                loader_label.pack(expand=True, fill='both')
                # Recherche des apps dans un thread pour ne pas bloquer l'UI
                def update_apps():
                    self.available_apps = self.find_installed_apps()
                    self.filtered_apps = self.available_apps.copy()
                    self.after(0, self.refresh_lists)
                threading.Thread(target=update_apps, daemon=True).start()
            ttk.Button(win, text=_["save_paths"] if "save_paths" in _ else "Sauvegarder", command=save_and_close, style='Green.TButton').pack(pady=10)

        def open_manual_app_selector(self):
            # Ouvre une fenêtre listant toutes les applis installées sur l'OS, indépendamment des dossiers à scanner
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
                apps_by_drive = defaultdict(list)
                for app in all_apps:
                    drive = os.path.splitdrive(app)[0].upper() if sys.platform.startswith('win') else os.path.dirname(app)
                    apps_by_drive[drive].append(app)
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
                    for drive in sorted(apps_by_drive.keys()):
                        drive_label = ttk.Label(frame, text=drive if drive else '(?)', background="#23272e", foreground="#eb8f34", font=("Segoe UI", 11, "bold"))
                        drive_label.grid(row=row, column=0, sticky='w', pady=(10,2))
                        row += 1
                        for app in sorted(apps_by_drive[drive], key=lambda p: os.path.basename(p).lower()):
                            var = tk.BooleanVar(value=app in self.selected_apps)
                            check_vars[app] = var
                            cb = ttk.Checkbutton(frame, text=os.path.basename(app), variable=var, style='TCheckbutton')
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
except Exception as e:
    logging.error(f"Fatal error at import or init: {e}", exc_info=True)
    raise
