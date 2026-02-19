#!/bin/bash
# Utilisation : ./run.sh pour le mode fenêtré ou ./run.sh --fs pour le kart

source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

# On passe tous les arguments reçus par le script au programme python
python3 main.py "$@"