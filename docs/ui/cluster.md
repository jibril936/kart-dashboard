# CLUSTER screen: architecture, gauge et kart central

## Où se trouve chaque composant

- **Écran CLUSTER (page 1)**: `src/ui/cluster_screen.py`
- **Gauge legacy (ancien widget custom)**: `src/ui/components/circular_gauge.py`
- **Gauge vendorisée (tierce partie)**: `src/ui/third_party/analoggaugewidget/analoggaugewidget.py`
- **Licence gauge vendorisée**: `src/ui/third_party/analoggaugewidget/LICENSE`
- **Wrapper projet (API stable pour CLUSTER)**: `src/ui/components/speed_gauge_oem.py`
- **Widget kart top-view (roues avant animées)**: `src/ui/components/kart_top_view_widget.py`
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
- `set_style(...)` (override ciblé des couleurs/ticks/angle/needle via le wrapper)

## Kart top-view (centre) : quoi modifier

Le rendu du kart est encapsulé dans `src/ui/components/kart_top_view_widget.py`.

### 1) Angles et braquage
- Clamp visuel: `STEER_VISUAL_CLAMP_DEG`
- Effet type Ackermann: `ACKERMANN_FACTOR`

### 2) Animation fluide des roues avant
- Animation: `QPropertyAnimation` sur la propriété `steerAngleDeg`
- Durées: `STEER_ANIM_MIN_MS` / `STEER_ANIM_MAX_MS`
- Easing: `QEasingCurve.Type.OutCubic`

### 3) Géométrie des roues
Dans `_draw_kart(...)` et `_draw_wheel(...)`:
- positions roues avant/arrière
- pivot de rotation (variable `pivot_x`)
- dimensions pneus (`QRectF(-8, -18, 16, 36)`)

### 4) Couleurs et intégration thème
Couleurs principales dans:
- fond plaque + glow
- carrosserie
- pneus / accents

Pour une harmonisation future, aligner les hex avec `src/ui/theme.py`.

## Intégration CLUSTER (limité écran CLUSTER)

- Le remplacement gauge se fait uniquement dans `src/ui/cluster_screen.py` via `SpeedGaugeOEM`.
- Le kart central est injecté via `CenterPanel` (`src/ui/components/center_panel.py`) sans ajout de nouveaux widgets/informations.

## Mini guide “je modifie moi-même”

1. Tester rapidement en mode normal.
2. Ajuster les paramètres dans le fichier vendorisé (angles/couleurs/ticks).
3. Vérifier le rendu en fallback legacy (`KART_SPEED_GAUGE_IMPL=legacy`) pour comparaison.
4. Valider les scénarios (`acceleration`, `battery_drop`, `overheat`, `sensor_ko`).
5. Harmoniser ensuite les couleurs avec `src/ui/theme.py`.
