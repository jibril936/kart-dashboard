# Kart Dashboard Pro V3

Dashboard haute performance pour Raspberry Pi 4, architecturé pour le temps réel et la modularité.

## Vue d'ensemble

Kart Dashboard Pro V3 est une application orientée exploitation embarquée, conçue pour afficher des données véhicule en temps réel avec une architecture claire et maintenable.

Principes clés :
- **Traitement non bloquant** des flux capteurs.
- **Simulation intégrée** pour accélérer le développement.
- **État applicatif centralisé** pour garantir la cohérence des données.
- **Interface découplée** pour faciliter l'évolution de l'UI.

## Requirements

Dépendances Python minimales :
- **PyQt6**

Voir le fichier `requirements.txt` pour la liste complète et les versions.

## Installation

### 1) Cloner le dépôt

```bash
git clone <url-du-repo>
cd kart-dashboard
```

### 2) Créer un environnement virtuel Python

```bash
python3 -m venv .venv
```

### 3) Activer l'environnement virtuel

- Linux/macOS :

```bash
source .venv/bin/activate
```

- Windows (PowerShell) :

```powershell
.venv\Scripts\Activate.ps1
```

### 4) Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Lancement

Depuis la racine du projet :

```bash
python main.py
```

## Documentation technique

- Architecture détaillée : `docs/architecture.md`
