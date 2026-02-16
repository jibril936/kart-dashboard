from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel
from qtpy.QtCore import Qt

class TemperatureWidget(QWidget):
    def __init__(self, label="TEMP", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # ON AJOUTE CECI : Marges à zéro
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        
        self.title_label = QLabel(label)
        # ... le reste ne change pas ...
        self.title_label.setStyleSheet("color: #888888; font-size: 14px; font-family: 'Orbitron';")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.val_label = QLabel("-- °C")
        self.val_label.setStyleSheet("color: white; font-size: 28px; font-family: 'Orbitron'; font-weight: bold;")
        self.val_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.val_label)

    def set_value(self, temp):
        self.val_label.setText(f"{temp:.0f} °C")
        # Alerte visuelle : Rouge si le moteur ou la batterie surchauffe (>75°C)
        color = "#FF3232" if temp > 75 else "white"
        self.val_label.setStyleSheet(f"color: {color}; font-size: 28px; font-family: 'Orbitron'; font-weight: bold;")