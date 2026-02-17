from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from qtpy.QtCore import Qt, Slot
from src.ui.components.battery_elements import BMSSummaryCard, BatteryIcon

class ExpertPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        
        # Données locales pour rafraîchir la carte sommaire
        self.v_tot = 0.0
        self.delta = 0.0
        self.v_min = 0.0
        self.v_max = 0.0
        
        # Configuration visuelle pour la Raspberry Pi
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        
        self.setup_ui()
        self.setup_overlay()
        self.connect_signals()

    def setup_ui(self):
        """Structure de base avec 4 zones (Grille 2x2)."""
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(30, 30, 30, 30)
        self.grid.setSpacing(20)

        # --- ZONE 1 : BMS (Haut Gauche) ---
        self.bms_card = BMSSummaryCard(self)
        self.bms_card.clicked.connect(self.show_overlay)
        self.grid.addWidget(self.bms_card, 0, 0)

        # --- ZONE 2 : PLACEHOLDER CHARGE (Haut Droite) ---
        self.grid.addWidget(self._make_placeholder("CHARGING (EVSE)"), 0, 1)

        # --- ZONE 3 : PLACEHOLDER MOTEUR (Bas Gauche) ---
        self.grid.addWidget(self._make_placeholder("DRIVE SYSTEM"), 1, 0)

        # --- ZONE 4 : PLACEHOLDER TELEMETRIE (Bas Droite) ---
        self.grid.addWidget(self._make_placeholder("TELEMETRY / G-FORCE"), 1, 1)

    def setup_overlay(self):
        """Fenêtre de détail des 16 cellules (cachée par défaut)."""
        self.overlay = QFrame(self)
        # On force la taille pour couvrir tout l'écran du dashboard
        self.overlay.setGeometry(0, 0, 1024, 600) 
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 245); border: none;")
        self.overlay.hide()
        
        over_layout = QVBoxLayout(self.overlay)
        over_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header de l'overlay (Titre + Bouton Fermer)
        header = QHBoxLayout() # <--- Corrigé : QHBoxLayout est maintenant importé
        title = QLabel("DETAILED CELL MONITOR")
        title.setStyleSheet("color: #00FFFF; font-family: 'Orbitron'; font-size: 22px; font-weight: bold;")
        
        close_btn = QPushButton("CLOSE [X]")
        close_btn.setFixedSize(120, 45)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                font-family: 'Orbitron';
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:pressed { background-color: #555555; }
        """)
        close_btn.clicked.connect(self.overlay.hide)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        over_layout.addLayout(header)
        over_layout.addSpacing(30)

        # Grille des 16 BatteryIcons
        self.cell_grid = QGridLayout()
        self.cell_grid.setSpacing(15)
        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i + 1)
            self.cell_widgets.append(icon)
            self.cell_grid.addWidget(icon, i // 8, i % 8)
        
        over_layout.addLayout(self.cell_grid)
        over_layout.addStretch()

    def _make_placeholder(self, text):
        """Crée un cadre vide pour les futures fonctions des camarades."""
        f = QFrame()
        f.setStyleSheet("border: 2px dashed #222222; border-radius: 15px;")
        l = QVBoxLayout(f)
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #333333; font-family: 'Orbitron'; font-size: 14px;")
        lbl.setAlignment(Qt.AlignCenter)
        l.addWidget(lbl)
        return f

    def show_overlay(self):
        """Affiche le détail des cellules par-dessus la page."""
        self.overlay.show()
        self.overlay.raise_() # S'assure qu'il passe au premier plan

    def connect_signals(self):
        """Branchement des données du Store."""
        self.store.pack_voltage_changed.connect(self._on_v)
        self.store.cell_delta_v.connect(self._on_d)
        self.store.cell_min_v.connect(self._on_min)
        self.store.cell_max_v.connect(self._on_max)
        self.store.cell_voltages_changed.connect(self._on_cells)

    @Slot(float)
    def _on_v(self, v): self.v_tot = v; self._refresh()
    @Slot(float)
    def _on_d(self, d): self.delta = d; self._refresh()
    @Slot(float)
    def _on_min(self, m): self.v_min = m; self._refresh()
    @Slot(float)
    def _on_max(self, m): self.v_max = m; self._refresh()

    @Slot(list)
    def _on_cells(self, v_list):
        """Met à jour les 16 petites piles quand le BMS envoie les tensions."""
        for i, v in enumerate(v_list):
            if i < len(self.cell_widgets):
                self.cell_widgets[i].set_voltage(v)

    def _refresh(self):
        """Met à jour le bloc de résumé BMS."""
        self.bms_card.update_data(self.v_tot, self.delta, self.v_min, self.v_max)