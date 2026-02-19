#!/bin/bash
# Utilisation : ./run.sh (fenêtré) ou ./run.sh --fs (kart plein écran)

# 1. On dit à X11 d'afficher sur l'écran local de la Pi
export DISPLAY=:0

# 2. On se place dans le dossier du script pour éviter les erreurs de chemin
cd "$(dirname "$0")"

# 3. Activation de l'environnement virtuel
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Erreur : Environnement virtuel .venv non trouvé."
    exit 1
fi

# 4. On ajoute le dossier actuel au chemin Python
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 5. Lancement avec les arguments passés au script
python3 main.py "$@"