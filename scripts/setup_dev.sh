#!/bin/bash
# Script d'installation et de configuration automatique pour memApp (dev)
set -e

# Installation des dépendances principales et dev
pip install --upgrade pip
pip install .[dev]

# Initialisation des outils de qualité
black src/ --check || black src/
flake8 src/
mypy src/

# Lancement des tests
pytest --maxfail=1 --disable-warnings

# Rapport de couverture
coverage run -m pytest
coverage report -m
coverage html

# Message de fin
echo "\nConfiguration et vérification terminées. Rapport de couverture disponible dans htmlcov/index.html."
