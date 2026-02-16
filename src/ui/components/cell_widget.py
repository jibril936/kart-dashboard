from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel
from qtpy.QtGui import QPainter, QColor, QPen
from qtpy.QtCore import Qt

class CellWidget(QWidget):
    def __init__(self, cell_id, parent=None):
        super().__init__(parent)
        self.cell_id = cell_id
        self.voltage = 3.6
        self.setFixedSize(70, 110) # Format vertical
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(1)
        
        self.volt_label = QLabel("3.60V")
        self.volt_label.setStyleSheet("color: white; font-size: 13px; font-family: 'Orbitron'; font-weight: bold;")
        self.volt_label.setAlignment(Qt.AlignCenter)
        
        self.id_label = QLabel(f"#{cell_id}")
        self.id_label.setStyleSheet("color: #666666; font-size: 9px; font-family: 'Orbitron';")
        self.id_label.setAlignment(Qt.AlignCenter)
        
        self.layout.addStretch()
        self.layout.addWidget(self.volt_label)
        self.layout.addWidget(self.id_label)

    def set_voltage(self, voltage):
        self.voltage = voltage
        self.volt_label.setText(f"{voltage:.2f}V")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond de la barre
        w, h = 12, 60
        x, y = (self.width() - w) // 2, 5
        
        painter.setBrush(QColor(40, 40, 40))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRoundedRect(x, y, w, h, 3, 3)
        
        # Remplissage (basé sur 2.8V - 4.2V)
        ratio = max(0, min(1, (self.voltage - 2.8) / (4.2 - 2.8)))
        fill_h = int(ratio * h)
        
        color = QColor(0, 255, 127) # Vert
        if self.voltage < 3.2: color = QColor(255, 50, 50) # Rouge
        elif self.voltage < 3.4: color = QColor(255, 150, 0) # Orange
        
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y + (h - fill_h), w, fill_h)