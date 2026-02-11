# Kart Dashboard – EV Cluster Preview

Refonte orientée "instrument cluster" avec deux écrans :

- **Drive / Conduite** (minimal, lisible à distance)
- **Details / Pit** (graphes + historique alertes + stats)

## Inspirations design

- Audi Virtual Cockpit (speed + power/recup + warnings)
- Porsche Taycan (mode "Pure" minimal)
- Tesla Model 3 (hiérarchie simple)

## Architecture

```text
src/
  core/
    types.py        # modèles d'état + alertes
    alerts.py       # règles d'alertes (INFO/WARNING/CRITICAL)
    store.py        # StateStore (single source of truth)
  services/
    base.py         # DataService injectable
    fake.py         # FakeDataService + scénarios demo
    poller.py       # acquisition data (QThread + QTimer)
  ui/
    components/     # widgets réutilisables (gauge, batterie, alertes, etc.)
    drive_screen.py
    details_screen.py
    main_window.py
    theme.py
  config/loader.py
  main.py
```

## Scénarios demo

```bash
./run.sh --demo --scenario normal
./run.sh --demo --scenario acceleration
./run.sh --demo --scenario battery_drop
./run.sh --demo --scenario overheat
./run.sh --demo --scenario sensor_ko
```

## Debug / logging

```bash
KART_LOG_LEVEL=DEBUG ./run.sh --demo
DEBUG=1 ./run.sh
```

## Notes performance

- Pas de re-création de widgets au tick
- StateStore unique + signal `state_changed`
- Lissage léger sur l'aiguille RPM
- Graphes pyqtgraph activés si installés, fallback sinon
