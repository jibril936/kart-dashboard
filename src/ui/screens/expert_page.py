from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from qtpy.QtCore import Qt, Slot
from src.ui.components.battery_elements import BMSSummaryCard, BatteryIcon

class ExpertPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        
        self.v_tot, self.delta, self.v_min, self.v_max = 0.0, 0.0, 0.0, 0.0
        
        self.setup_ui()
        self.setup_overlay() # L'overlay est créé ici
        self.connect_signals()

    def setup_ui(self):
        """La page Expert de base (Grille 2x2)."""
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(20, 20, 20, 20)
        
        self.bms_card = BMSSummaryCard(self)
        self.bms_card.clicked.connect(self.show_overlay)
        self.grid.addWidget(self.bms_card, 0, 0)
        
        self.grid.addWidget(self._make_placeholder("CHARGING (EVSE)"), 0, 1)
        self.grid.addWidget(self._make_placeholder("DRIVE SYSTEM"), 1, 0)
        self.grid.addWidget(self._make_placeholder("TELEMETRY"), 1, 1)

    def setup_overlay(self):
        """L'overlay qui s'affiche au clic."""
        self.overlay = QFrame(self)
        self.overlay.hide()
        # Opacité pour voir un peu le fond mais pas trop pour rester lisible
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 250); border: none;")
        
        # Layout vertical principal de l'overlay
        over_layout = QVBoxLayout(self.overlay)
        over_layout.setContentsMargins(30, 20, 30, 20)
        
        # 1. Header (Fixe en haut)
        header = QHBoxLayout()
        lbl = QLabel("CELLS DETAILED MONITOR")
        lbl.setStyleSheet("color: cyan; font-family: Orbitron; font-size: 20px; font-weight: bold;")
        
        self.close_btn = QPushButton("CLOSE [X]")
        self.close_btn.setFixedSize(120, 45)
        self.close_btn.setStyleSheet("background: #222; color: white; border-radius: 8px; font-family: Orbitron;")
        self.close_btn.clicked.connect(self.overlay.hide)
        
        header.addWidget(lbl)
        header.addStretch()
        header.addWidget(self.close_btn)
        over_layout.addLayout(header)

        # 2. Grille 4x4 (Plus compacte verticalement que 2x8)
        self.cell_grid_container = QWidget()
        self.cell_grid = QGridLayout(self.cell_grid_container)
        self.cell_grid.setSpacing(15)
        
        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i+1)
            self.cell_widgets.append(icon)
            # Grille 4x4
            self.cell_grid.addWidget(icon, i // 4, i % 4, Qt.AlignCenter)
        
        over_layout.addWidget(self.cell_grid_container, 1) # Priorité à la grille
        over_layout.addStretch() # Pousse tout vers le haut

    def resizeEvent(self, event):
        """Indispensable pour que l'overlay occupe 100% de la fenêtre."""
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def show_overlay(self):
        self.overlay.show()
        self.overlay.raise_()

    def _make_placeholder(self, t):
        f = QFrame(); f.setStyleSheet("border: 1px dashed #333; border-radius: 15px;")
        l = QVBoxLayout(f); l.addWidget(QLabel(t, alignment=Qt.AlignCenter, styleSheet="color:#444; font-family:Orbitron;"))
        return f

    def connect_signals(self):
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
        for i, v in enumerate(v_list):
            if i < 16: self.cell_widgets[i].set_voltage(v)

    def _refresh(self):
        self.bms_card.update_data(self.v_tot, self.delta, self.v_min, self.v_max)