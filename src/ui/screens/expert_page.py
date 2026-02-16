from qtpy.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from qtpy.QtCore import Qt, Slot
from src.ui.components.cell_widget import CellWidget

class ExpertPage(QWidget): # <--- Le nom doit être EXACTEMENT celui-là
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.cells = []
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setStyleSheet("background-color: black;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header avec Delta V
        header = QHBoxLayout()
        title = QLabel("BMS CELLS MONITOR")
        title.setStyleSheet("color: #00FFFF; font-size: 22px; font-family: 'Orbitron'; font-weight: bold;")
        
        self.delta_label = QLabel("ΔV: 0.000V")
        self.delta_label.setStyleSheet("color: white; font-size: 20px; font-family: 'Orbitron';")
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.delta_label)
        self.main_layout.addLayout(header)
        
        # Grille 2x8 pour les 16 cellules
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        for i in range(16):
            cell = CellWidget(i + 1)
            self.cells.append(cell)
            self.grid.addWidget(cell, i // 8, i % 8)
            
        self.main_layout.addLayout(self.grid)
        self.main_layout.addStretch()

    def connect_signals(self):
        # Vérifie que ton Store émet bien 'cell_voltages_changed'
        if hasattr(self.store, 'cell_voltages_changed'):
            self.store.cell_voltages_changed.connect(self._update_all_cells)

    @Slot(list)
    def _update_all_cells(self, voltages):
        if len(voltages) >= 16:
            for i in range(16):
                self.cells[i].set_voltage(voltages[i])
            
            diff = max(voltages) - min(voltages)
            self.delta_label.setText(f"ΔV: {diff:.3f}V")
            # Alerte si déséquilibre > 50mV
            color = "#FF8800" if diff > 0.050 else "white"
            self.delta_label.setStyleSheet(f"color: {color}; font-size: 20px; font-family: 'Orbitron';")