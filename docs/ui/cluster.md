# CLUSTER screen: architecture et réglages speed gauge

## Où se trouve chaque composant

- **Écran CLUSTER (page 1)**: `src/ui/cluster_screen.py`
- **Gauge legacy (ancien widget custom)**: `src/ui/components/circular_gauge.py`
- **Gauge vendorisée (tierce partie)**: `src/ui/third_party/analoggaugewidget/analoggaugewidget.py`
- **Wrapper projet (API stable pour CLUSTER)**: `src/ui/components/speed_gauge_oem.py`
- **Thème global PyQt/QSS**: `src/ui/theme.py`
- **Notices/licence tierce partie**:
  - `THIRD_PARTY_NOTICES.md`
  - `third_party/analoggaugewidget/LICENSE`

## Sélecteur rapide (fallback legacy)

Dans `src/ui/cluster_screen.py`, la jauge utilisée est sélectionnée via:

- `KART_SPEED_GAUGE_IMPL=oem` (par défaut) → wrapper `SpeedGaugeOEM`
- `KART_SPEED_GAUGE_IMPL=legacy` → widget `CircularGauge`

Exemple:

```bash
export KART_SPEED_GAUGE_IMPL=legacy
python src/main.py --demo --scenario normal
```

## Paramètres modifiables (nouvelle jauge)

### 1) Angles min/max de l’arc
Dans `src/ui/third_party/analoggaugewidget/analoggaugewidget.py`:
- `scale_angle_start_value` (angle de départ)
- `scale_angle_size` (ouverture totale)

Méthodes associées:
- `setScaleStartAngle(...)`
- `setTotalScaleAngleSize(...)`

### 2) Style aiguille (longueur/épaisseur)
Toujours dans `paintEvent(...)` du fichier vendorisé:
- `pointer_radius` (longueur)
- `QPen(..., 7.0, ...)` glow
- `QPen(..., 3.6, ...)` trait principal
- `tip_w` (largeur de la pointe)

### 3) Ticks (majeurs/mineurs)
- `scala_main_count` (nombre de divisions majeures)
- `scala_subdiv_count` (mineurs entre majeurs)
- Méthodes:
  - `setScalaMainCount(...)`
  - `setScalaSubDivCount(...)`

Dans le wrapper `src/ui/components/speed_gauge_oem.py`, ces valeurs sont mappées depuis:
- `major_tick_step`
- `minor_ticks_per_major`

### 4) Couleurs (en lien avec le thème)
Dans le widget vendorisé, les principales variables:
- `gauge_color_outer`, `gauge_color_inner`
- `gauge_color_active_start`, `gauge_color_active_end`
- `tick_major_color`, `tick_minor_color`
- `label_color`, `value_color`, `unit_color`
- `needle_color`, `needle_glow_color`

Pour harmoniser avec le thème, aligner ces couleurs avec les teintes de `src/ui/theme.py`.

### 5) Tailles de police
Dans `paintEvent(...)` du fichier vendorisé, modifier les `QFont(...)` pour:
- labels de graduation
- titre
- valeur centrale
- unité

## Mapping vitesse CLUSTER

Le mapping CLUSTER est fixé à **0–60 km/h** dans `src/ui/cluster_screen.py`:
- `SPEED_MIN_KMH = 0`
- `SPEED_MAX_KMH = 60`

Le wrapper expose:
- `set_value(...)`
- `set_speed(...)`
- `set_range(...)`

## Mini guide “je modifie moi-même”

1. Tester rapidement en mode normal.
2. Ajuster les paramètres dans le fichier vendorisé (angles/couleurs/ticks).
3. Vérifier le rendu en fallback legacy (`KART_SPEED_GAUGE_IMPL=legacy`) pour comparaison.
4. Valider les scénarios (`acceleration`, `battery_drop`, `overheat`, `sensor_ko`).
5. Harmoniser ensuite les couleurs avec `src/ui/theme.py`.
