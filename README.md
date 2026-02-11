# Kart Dashboard — Cluster + TECH (PyQt6)

Application desktop PyQt6 avec deux pages:

- **CLUSTER / CONDUITE** (style tableau de bord)
- **TECH / DIAGNOSTICS** (télémétrie détaillée + alert center)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement demo

```bash
python src/main.py --demo --scenario normal
python src/main.py --demo --scenario battery_drop
python src/main.py --demo --scenario overheat
```

Scénarios disponibles:

- `normal`
- `battery_drop`
- `overheat`
- `sensor_ko`
