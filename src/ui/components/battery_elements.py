from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QProgressBar
from qtpy.QtGui import QPainter, QColor, QPen, QFont
from qtpy.QtCore import Qt, QRect, Signal

class CircularBatteryWidget(QWidget):
    """Cercle central SOC pour la Page 1 (Drive)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.soc = 0

    def update_status(self, soc):
        self.soc = soc
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond
        p.setPen(QPen(QColor(30, 30, 30), 14))
        p.drawArc(20, 20, 180, 180, 0, 360 * 16)
        
        # Arc de couleur
        color = QColor(0, 255, 150) if self.soc > 20 else QColor(255, 50, 50)
        p.setPen(QPen(color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        span = int((self.soc / 100.0) * 360 * 16)
        p.drawArc(20, 20, 180, 180, 90 * 16, -span)
        
        # Pourcentage
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 48, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.soc}%")

class BMSSummaryCard(QFrame):
    """Résumé BMS avec barres Min/Max (Page 2)."""
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 240)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QFrame { background-color: #0A0A0A; border: 1px solid #222; border-radius: 15px; }")
        
        layout = QVBoxLayout(self)
        self.val_v = QLabel("0.0 V")
        self.val_v.setStyleSheet("color: white; font-size: 38px; font-weight: bold; border:none; font-family: 'Orbitron';")
        layout.addWidget(QLabel("BMS HEALTH", styleSheet="color:cyan; font-size:10px; border:none;"))
        layout.addWidget(self.val_v)
        
        self.val_delta = QLabel("ΔV: 0.000 V")
        self.val_delta.setStyleSheet("color: #00FF7F; font-size: 16px; border:none;")
        layout.addWidget(self.val_delta)

        self.min_bar = self._add_bar(layout, "MIN")
        self.max_bar = self._add_bar(layout, "MAX")
        layout.addStretch()

    def _add_bar(self, layout, name):
        row = QHBoxLayout()
        lbl = QLabel(name); lbl.setStyleSheet("color:#555; font-size:9px; border:none;")
        bar = QProgressBar(); bar.setFixedHeight(4); bar.setTextVisible(False)
        bar.setStyleSheet("QProgressBar { background:#111; border:none; } QProgressBar::chunk { background:cyan; }")
        val = QLabel("0.00V"); val.setStyleSheet("color:white; font-size:11px; border:none;")
        row.addWidget(lbl); row.addWidget(bar); row.addWidget(val)
        layout.addLayout(row)
        return (bar, val)

    def mousePressEvent(self, event): self.clicked.emit()

    def update_data(self, v, delta, v_min, v_max):
        self.val_v.setText(f"{v:.1f} V")
        self.val_delta.setText(f"ΔV: {delta:.3f} V")
        for bar, label, val in [(self.min_bar[0], self.min_bar[1], v_min), (self.max_bar[0], self.max_bar[1], v_max)]:
            bar.setValue(int(((val - 2.8) / 1.4) * 100))
            label.setText(f"{val:.2f}V")

class BatteryIcon(QWidget):
    """Icône ultra-compacte pour tenir en grille 4x4."""
    def __init__(self, cell_id, parent=None):
        super().__init__(parent)
        self.voltage = 3.6
        self.cell_id = cell_id
        self.setFixedSize(50, 80) # <--- Taille réduite ici

    def set_voltage(self, v): 
        self.voltage = v
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Corps de la pile (plus fin)
        p.setPen(QPen(QColor(80, 80, 80), 1))
        p.drawRoundedRect(12, 5, 26, 50, 3, 3)
        
        # Remplissage
        ratio = max(0, min(1, (self.voltage - 2.8) / 1.4))
        color = QColor(0, 255, 150) if self.voltage > 3.2 else QColor(255, 50, 50)
        p.setBrush(color)
        h = int(ratio * 46)
        p.drawRect(14, 55 - h, 22, h)
        
        # Texte (Cell ID en haut, Voltage en bas)
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 7))
        p.drawText(QRect(0, 0, 50, 10), Qt.AlignCenter, f"#{self.cell_id}")
        
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 8))
        p.drawText(QRect(0, 58, 50, 20), Qt.AlignCenter, f"{self.voltage:.2f}V")