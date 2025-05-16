# Changelog / Notes de version

## [0.0.3] - 2025-05-16

### Nouveautés et améliorations majeures
- Ajout UI
- Ajout du support multi-langue, loader, et configuration dynamique des dossiers à scanner.
- Ajout d'une fenêtre de sélection manuelle des applications installées, indépendante des dossiers à scanner, compatible Windows, macOS et Linux.
- Détection multiplateforme :
  - Windows : détection via le module Python `winapps` (affiche un message si non installé).
  - macOS : détection des `.app` dans /Applications et ~/Applications, et Homebrew casks.
  - Linux : détection des fichiers `.desktop` et paquets installés (dpkg).
- Loader visuel lors des scans longs (UI non bloquée).
- Amélioration de la robustesse de la configuration et de l'expérience utilisateur.
- Mise à jour du setup.py : tous les fichiers nécessaires sont inclus, dépendances et exclusions à jour, note sur la dépendance à `winapps`.

### Correctifs

### Notes
- Pour la détection complète des applications installées sous Windows, le module Python `winapps` doit être installé (`pip install winapps`).
- Voir README.md pour plus d'informations sur l'installation et la configuration multiplateforme.

---

## [0.0.1] - 2022-06
- Première version stable
