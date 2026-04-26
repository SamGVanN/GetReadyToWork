#!/bin/bash
# Script d'installation automatique pour le développement (Linux/Mac)
set -e

# Change to project root
cd "$(dirname "$0")/.."

if ! command -v python3 &> /dev/null; then
  echo "Python3 n'est pas installé. Veuillez l'installer d'abord."
  exit 1
fi

echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

echo "Installation des dépendances Python..."
pip install -r installers/requirements-linux.txt

echo "Installation terminée. Vous pouvez lancer le paramétrage avec :"
echo "source venv/bin/activate"
echo "python -m src.app_configurator.ParametrageGetReadyToWork"
