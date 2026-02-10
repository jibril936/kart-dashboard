# Kart Dashboard (PyQt6)

Dashboard tactile plein écran pour kart électrique (Raspberry Pi 4), avec architecture découplée:

`DataSource -> TelemetryModel -> UI`

L'UI ne dépend pas de la source matérielle (simulated / i2c aujourd'hui, serial/can/ble demain).

## Structure

```text
src/
  config/
    loader.py              # AppConfig + lecture YAML
  data/
    worker.py              # polling en arrière-plan (QThread + QTimer)
    logger.py              # logger CSV optionnel
    sources/
      base.py              # interface DataSource
      simulated.py         # SimulatedDataSource
      i2c.py               # I2CDataSource (stub prêt)
  models/
    telemetry.py           # dataclass Telemetry unique
    telemetry_model.py     # règles alertes / transformation
  ui/
    dashboard.py           # fenêtre + navigation Drive/Diag
    drive_view.py          # vue lisible conduite
    diag_view.py           # vue diagnostic + graphes
  main.py
config/
  config.example.yaml
run.sh
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel
python -m pip install -r requirements.txt
```

Optionnel I2C:

```bash
python -m pip install smbus2
```

## Configuration

Copiez l'exemple:

```bash
cp config/config.example.yaml config/config.yaml
```

Paramètres importants:

- `source`: `simulated` ou `i2c`
- `refresh_hz`: fréquence du worker (ex: 20 Hz)
- `fullscreen`: plein écran
- `debug`: mode fenêtré
- `i2c.bus` / `i2c.address`
- `alerts.*`: seuils d'alertes UI
- `logging.enabled` / `logging.path`: CSV optionnel

Override via variable d'environnement:

```bash
KART_CONFIG=/chemin/config.yaml ./run.sh
```

## Run

```bash
./run.sh
```

Mode debug (fenêtré):

```bash
DEBUG=1 ./run.sh
```

## UI

- **DriveView**: vitesse très grande, SOC, puissance/courant, températures, alertes visibles + état source (OK/TIMEOUT/ERROR).
- **DiagView**: valeurs brutes + mini-graphes (pyqtgraph), accessible via bouton tactile ⚙️, retour via **Back**.

## Extensibilité

Pour ajouter Serial/CAN/BLE:

1. Créer une nouvelle classe implémentant `DataSource` (`start/stop/read`).
2. L'ajouter dans `build_source()` de `src/main.py`.
3. Aucun changement UI requis.
