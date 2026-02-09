# Kart Dashboard (PyQt6)

GUI dashboard for a kart (target: Raspberry Pi 4).

## Structure
```
src/
  config/          # chargement configuration
  data/            # acquisition + logging
    sources/       # drivers (simulated, i2c)
  models/          # dataclasses
  ui/              # interface PyQt6
config/            # exemples de configuration
```

## Setup
Dépendances principales : PyQt6, pyqtgraph, PyYAML.
Optionnel : `smbus2` si vous utilisez la source I2C.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel
python -m pip install -r requirements.txt
```

> Optionnel si vous utilisez l'I2C :
```bash
python -m pip install smbus2
```

## Configuration
Copiez l'exemple et adaptez les paramètres :
```bash
cp config/config.example.yaml config/config.yaml
```

Variables disponibles :
- `source`: `simulated` ou `i2c`
- `refresh_hz`: fréquence de rafraîchissement UI
- `fullscreen`: plein écran
- `debug`: force le mode fenêtré
- `i2c.bus`, `i2c.address`: bus + adresse I2C
- `logging.enabled`, `logging.path`: logging CSV (optionnel)

Vous pouvez aussi pointer vers un autre fichier via :
```
KART_CONFIG=/chemin/vers/config.yaml
```

## Run
```bash
./run.sh
```

Mode debug (fenêtré) :
```bash
DEBUG=1 ./run.sh
```
