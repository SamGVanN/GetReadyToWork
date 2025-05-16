#!/bin/bash
# Script d'installation automatique pour Linux/Mac
set -e

if ! command -v python3 &> /dev/null; then
  echo "Python3 n'est pas installé. Veuillez l'installer d'abord."
  exit 1
fi

if ! command -v pip3 &> /dev/null; then
  echo "pip3 n'est pas installé. Veuillez l'installer d'abord."
  exit 1
fi

echo "Installation des dépendances Python..."
pip3 install --user -r requirements-linux.txt

echo "Installation terminée. Vous pouvez lancer le paramétrage avec :"
echo "python3 src/ParametrageGetReadyToWork.py"
