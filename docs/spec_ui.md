# UI/UX Specification (v1.1)

## Global Constraints

- **Framework**: Python + PyQt6
- **UI**: Dark mode, high contrast, touch-friendly
- **Target**: 1024x600 (min 800x480)
- **Performance**: pas de recréation de widgets au tick, update via store/state
- **Scope**: ne pas refactor l’architecture existante (store/services), seulement UI/UX
- **Pages**: 3 pages (CLUSTER, TECH, GRAPHS)

## Page Structure

| Page ID | Name | Role | Key Widgets |
|---|---|---|---|
| P1 | CLUSTER / Conduite | Infos critique conduite | Speed gauge + Kart visual + Power/Current + Battery/Motor/BattTemp + Warning strip |
| P2 | TECH / Diagnostics | Données détaillées | Tabs: BMS, Charge, Direction, Traction/Frein, Sensors |
| P3 | GRAPHS / ÉNERGIE | Analyse temps réel | Power(t), Energy(Wh), Sag(V), Cell Delta(mV), Batt Temp max(t) |

## Data Dictionary (v1.1)

### Conduite — P0 (toujours visible)

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Speed | Variateur / capteur vitesse | km/h | 0 | 60 | 10–20 Hz | A | Page 1 | Gauge speed (circular) |
| Battery pack voltage | BMS | V | 44 | 54 | 1–5 Hz | A | Page 1 | Battery bar + value |
| Battery pack current | BMS | A | -200 | +200 | 1–5 Hz | A | Page 1 | Power/Current gauge (semi) |
| Instant power (P = V×I) | Calcul (BMS V & I) | W / kW | -10kW | +10kW | 1–5 Hz | A | Page 1 | Power gauge / numeric |
| Motor temperature | Variateur / capteur moteur | °C | 0 | 120 | 1–5 Hz | A | Page 1 | Temp bar + value |
| Battery temperature (pack / max) | BMS | °C | 0 | 80 | 1–2 Hz | A | Page 1 | Small temp widget (value + mini bar) (idéalement affiché à côté de la batterie) |
| Brake state | Variateur / frein | bool | 0 | 1 | 10–20 Hz | A | Page 1 | Icon / lamp |

### Conduite — P1 (visible mais discret)

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Steering angle | Direction | ° | -35 | +35 | 10–20 Hz | B | Page 1 | Kart visual (front wheels rotate) + small numeric |
| Ultrasonic rear (1..3) distance | Capteurs ultrasons | m / cm | 0 | 4m | 5–10 Hz | B | Page 1 | 3 small indicators (only show if close) |
| Warnings (battery low / overtemp / sensor fail) | Règles | enum | — | — | 5–10 Hz | B | Page 1 | Top warning strip (icons) |

### TECH / Diagnostics — Page 2 (onglets)

#### Onglet 1 — BMS (pack)

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| SOC (si dispo) | BMS | % | 0 | 100 | 1–2 Hz | C | Page 2 | Big value + small trend |
| Pack voltage | BMS | V | 44 | 54 | 1–5 Hz | C | Page 2 | numeric + sparkline |
| Pack current | BMS | A | -200 | +200 | 1–5 Hz | C | Page 2 | numeric + sign (charge/discharge) |
| Pack power | calcul | W/kW | — | — | 1–5 Hz | C | Page 2 | numeric |
| BMS temperatures (T1/T2/MOS + max) | BMS | °C | 0 | 80 (MOS parfois 100) | 1–2 Hz | C | Page 2 | list / mini-bars (inclure “max batt temp” + détail T1/T2) |
| Cell voltages (list) | BMS | V | 2.5 | 4.3 | 1–2 Hz | C | Page 2 | grid/scroll list |
| Cell min / max / delta | calcul | V | 0 | 1 | 1–2 Hz | C | Page 2 | summary card |

#### Onglet 2 — Charge / Borne

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Charging state | BMS / charge | bool | 0 | 1 | 1–2 Hz | C | Page 2 | status badge |
| EVSE current | Borne | A | 0 | (à définir) | 1–2 Hz | C | Page 2 | numeric |
| EVSE frequency | Borne | Hz | 45 | 65 | 1–2 Hz | C | Page 2 | numeric |

#### Onglet 3 — Direction

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Steering pot voltage | Direction | V | 0 | 5 | 10–20 Hz | C | Page 2 | numeric + bar |
| Steering angle | Direction | ° | -35 | +35 | 10–20 Hz | C | Page 2 | numeric + gauge |
| Steering current | Direction | A | 0 | (à définir) | 10–20 Hz | C | Page 2 | numeric |

#### Onglet 4 — Traction / Frein

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Brake state | Variateur | bool | 0 | 1 | 10–20 Hz | C | Page 2 | badge |
| (Option) RPM | Variateur | rpm | 0 | 8000 | 10–20 Hz | C | Page 2 | numeric only (pas en conduite) |

#### Onglet 5 — Sensors

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Ultrasonic states | capteurs | bool | 0 | 1 | 5–10 Hz | C | Page 2 | list |
| Ultrasonic distances | capteurs | cm | 0 | 400 | 5–10 Hz | C | Page 2 | bars |

### Page 3 — GRAPHS / ÉNERGIE

#### Données & formules

- **Puissance instantanée**: `P(t) = Vpack(t) × Ipack(t)` → graphe ligne (W ou kW)
- **Énergie consommée**: `E(t) = ∫ P(t) dt` ; en pratique `E_Wh += P_W * dt_seconds / 3600` → graphe cumulatif (Wh)
- **Battery sag**: `sag = Vpack_idle_est - Vpack_loaded` ; simple version: `V_ref = max(Vpack) sur 30s quand I proche de 0` ; `sag = V_ref - Vpack` → graphe sag (V)
- **Qualité pack**: `delta_cell = Vcell_max - Vcell_min` → graphe delta (mV) + seuils (30–50mV warn, 80mV critical à calibrer)
- **Température batterie max**: `T_batt_max(t) = max(T1, T2, …)` → graphe ligne (°C) + seuils

| Nom | Source | Unité | Min | Max | Fréquence | Priorité | Page | Widget |
|---|---|---|---|---|---|---|---|---|
| Puissance instantanée P(t) | Calcul (Vpack × Ipack) | W / kW | — | — | 1–5 Hz | B | Page 3 | Line graph |
| Énergie consommée E(t) | Intégration de P(t) | Wh | 0 | — | 1–5 Hz | B | Page 3 | Cumulative graph |
| Battery sag | Calcul (V_ref - Vpack) | V | 0 | — | 1–5 Hz | B | Page 3 | Line graph + threshold |
| Delta cellule | Calcul (Vcell_max - Vcell_min) | mV | 0 | — | 1–2 Hz | B | Page 3 | Line graph + warn/critical bands |
| Température batterie max | BMS (max T1/T2/…) | °C | 0 | 100 | 1–2 Hz | B | Page 3 | Line graph + threshold |
