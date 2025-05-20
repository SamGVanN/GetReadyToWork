# Changelog / Notes de version

## [1.0.0] - 2025-05-20
### Added
- Build scripts pour Windows, Linux, macOS déplacés dans le dossier `tools/`.
- Centralisation du versioning dans `src/common/version.py` et génération automatique de `version_info.txt`.
- Import dynamique robuste pour les ressources i18n et les chemins de scan (compatibles dev/frozen, tous OS).
- Gestion centralisée de la configuration et des chemins de scan dans `src/common/config_manager.py`.
- Interface graphique moderne et multilingue (Tkinter, anglais/français auto).
- Sélection manuelle et automatique des applications à lancer, avec scan par dossiers configurables.

### Changed
- Suppression complète de cx_Freeze, seul PyInstaller est utilisé pour le packaging.
- Les scripts de build produisent toujours des dossiers de release propres à la racine du projet.
- Les chemins de scan par défaut sont chargés dynamiquement selon l'OS et le mode d'exécution.

### Fixed
- Problèmes d'import et de configuration en mode exécutable corrigés.
- Les chemins de scan et les ressources i18n sont toujours trouvés, quel que soit le mode d'exécution.

## Prochaines évolutions
- Prise en charge des icônes d'applications (affichage natif des icônes dans la liste, Windows/Mac/Linux)
- Export/import de la configuration utilisateur (partage facile entre machines)
- Support de profils multiples (plusieurs listes d'apps selon le contexte ou l'utilisateur)
- Ajout d'un mode "démarrage automatique" (lancement au boot ou à l'ouverture de session)
- Amélioration de la détection d'applications sur Linux (support Flatpak/Snap)
- Interface utilisateur personnalisable (thèmes, couleurs, etc.)
- Documentation utilisateur enrichie (FAQ)
---

## [0.0.4] - 2025-05-18
### Refactor & Robustification
- Refactor complet de la structure du projet pour robustesse et maintenabilité.
- Séparation du code GUI dans `src/app_configurator/GUI.py`.
- Centralisation de la gestion des fichiers de configuration dans `src/common/config_manager.py`.
- Tous les utilitaires partagés sont dans `src/common/utils.py`.
- Les imports sont robustes et compatibles mode script/module et mode exécutable (frozen).
- Le build cx_Freeze inclut tous les fichiers nécessaires (`common/`, etc.) pour les deux exécutables.
- Les instructions d'exécution recommandent désormais `python -m ...` pour le développement.
- README et setup.py mis à jour pour refléter la nouvelle structure et les bonnes pratiques.

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
