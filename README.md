# Kart Dashboard EV (Raspberry Pi)

Dashboard tactile pour kart électrique (Python + Qt), pensé pour un écran unique en conduite.

Architecture: `DataSource -> TelemetryModel -> UI`.

- Source télémétrie interchangeable (`simulated`, `i2c`, puis CAN/UART/UDP plus tard)
- UI découplée de la source matérielle
- Compatibilité **PyQt5 et PyQt6** via couche `src/qt_compat.py`
- `pyqtgraph` optionnel (fallback placeholder si non installé)
- Si I2C indisponible: fallback automatique en simulated + message clair

## Wireframe (texte)

### 1) Mode Conduite (principal)

```text
┌───────────────────────────────────────────────────────────────────────┐
│ SOURCE: OK/ERROR                                    [⚙ Diagnostic]   │
│                                                                       │
│                          72 km/h                                      │
│                                                                       │
│                      SOC 84 %                                         │
│                                                                       │
│  ┌──────────────────────┐   ┌──────────────────────┐                 │
│  │ Power                │   │ Current              │                 │
│  │ +12.4 kW / -regen    │   │ 54.2 A               │                 │
│  └──────────────────────┘   └──────────────────────┘                 │
│  ┌──────────────────────┐   ┌──────────────────────┐                 │
│  │ Températures         │   │ Alertes              │                 │
│  │ M 65 | I 54 | B 38   │   │ Surchauffe / capteur │                 │
│  └──────────────────────┘   └──────────────────────┘                 │
└───────────────────────────────────────────────────────────────────────┘
```

### 2) Mode Diagnostic (secondaire)

```text
┌───────────────────────────────────────────────────────────────────────┐
│ [⬅ Back]                                                              │
│                                                                       │
│ Voltage: 51.2V   Current: 43A   Power: 2.2kW   RPM: 5320             │
│ Throttle: 30%    Brake: 0%      Source: OK                           │
│                                                                       │
│ [Graphes pyqtgraph si dispo]                                          │
│ (sinon: placeholder "graphiques désactivés")                         │
└───────────────────────────────────────────────────────────────────────┘
```

## Thème UI recommandé

- **Dark mode** (`#0b0f1a`) pour limiter l’éblouissement
- Contraste élevé texte principal (`#F9FAFB`) / secondaire (`#9CA3AF`)
- Chiffres critiques en très gros (vitesse/SOC)
- Icônes + couleurs statut source/alertes (vert/orange/rouge)
- Interactions courtes et peu profondes (Drive ⇄ Diag)

## Structure code

```text
src/
  config/
    loader.py              # AppConfig + YAML
  data/
    worker.py              # polling async Qt (QThread + QTimer)
    logger.py              # export CSV optionnel
    sources/
      base.py              # interface DataSource
      simulated.py         # SimulatedDataSource
      i2c.py               # I2CDataSource + disponibilité
  models/
    telemetry.py           # modèle Telemetry unique
    telemetry_model.py     # règles alertes
  ui/
    dashboard.py           # navigation Drive/Diag
    drive_view.py          # vue conduite
    diag_view.py           # vue diagnostic + graphes optionnels
  qt_compat.py             # abstraction PyQt5/PyQt6
  main.py
```

### Ajouter une nouvelle source (CAN/UART/UDP/log)

1. Créer une classe implémentant `DataSource` (`start/stop/read`).
2. Ajouter le mapping dans `build_source()` (`src/main.py`).
3. Retourner des `Telemetry` cohérents (l’UI reste inchangée).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel
python -m pip install -r requirements.txt
```

Puis installer **une stack Qt**:

```bash
# Option A (souvent plus simple sur Raspberry Pi)
python -m pip install PyQt5

# Option B
python -m pip install PyQt6
```

Optionnel:

```bash
python -m pip install pyqtgraph smbus2
```

## Configuration

```bash
cp config/config.example.yaml config/config.yaml
```

Exemple:

- `source`: `simulated` ou `i2c`
- `refresh_hz`: ex. `20`
- `fullscreen`: `true`
- `debug`: `false`

Si config absente: defaults automatiques.

## Run

```bash
./run.sh
```

Mode debug:

```bash
DEBUG=1 ./run.sh
```

## Plan d’itération

- **MVP**: vue conduite lisible, simulated, alertes basiques, diag brut
- **V1**: intégration capteurs I2C/CAN, logs exportables, mini-trip
- **V2**: widgets EV avancés (power/regen meter dédié, SOC/range enrichi), historique événements, tuning UX conduite
