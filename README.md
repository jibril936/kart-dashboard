# Kart Dashboard — Cluster + TECH (PyQt6)

Application desktop PyQt6 avec 2 pages :
- **CLUSTER / CONDUITE**
- **TECH / DIAGNOSTICS**

## Setup (PC & Raspberry Pi identique)

> Clone recommandé en SSH

```bash
git clone git@github.com:jibril936/kart-dashboard.git
cd kart-dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commandes utiles

### 1) PC (Ubuntu/dev)

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD"
python src/main.py --demo --scenario normal
```

### 2) Raspberry Pi (local)

```bash
cd ~/kart-dashboard
source .venv/bin/activate
export PYTHONPATH="$PWD"
python src/main.py --demo --scenario normal
```

### 3) Raspberry Pi (lancer sur l’écran depuis SSH)

```bash
cd ~/kart-dashboard
source .venv/bin/activate
export PYTHONPATH="$PWD"
export DISPLAY=:0
export XAUTHORITY=/home/jibril/.Xauthority
python src/main.py --demo --scenario normal
```

> Adapte le chemin home si différent.
> Si l’app est lancée depuis SSH et ne s’affiche pas, vérifier que le bureau est ouvert sur la Pi.

## Lancement demo (scénarios disponibles)

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD"
python src/main.py --demo --scenario normal
python src/main.py --demo --scenario battery_drop
python src/main.py --demo --scenario overheat
python src/main.py --demo --scenario sensor_ko
```

## Debug rapide

```bash
python src/main.py -h
python -c "import PyQt6; print('PyQt6 OK')"
```

## Mise à jour du code

```bash
git pull
```
