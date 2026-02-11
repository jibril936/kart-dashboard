# Kart Dashboard — TECH MVP (PyQt6)

Application desktop PyQt6 pour afficher les **informations techniques véhicule**.

## Setup (conda)

```bash
conda create -n kart-tech python=3.12 -y
conda activate kart-tech
pip install -r requirements.txt
```

## Lancement demo

```bash
python -m src.main --demo --scenario normal
```

Scénarios prévus (MVP):

- `normal`
- `battery_drop`
- `overheat`
- `sensor_ko`

> Étape 1 livrée: socle app + écran TECH + fake data normal.
