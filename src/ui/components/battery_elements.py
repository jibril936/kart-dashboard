from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from qtpy.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from qtpy.QtCore import Qt, QRect, Signal

# --- LE RÉSUMÉ BMS (1/4 de la Page Expert) ---
class BMSSummaryCard(QFrame):
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 240)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame { background-color: #121212; border: 2px solid #222222; border-radius: 15px; }
            QLabel { border: none; font-family: 'Orbitron'; color: white; }
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("BMS HEALTH", styleSheet="color: #00FFFF; font-weight: bold; font-size: 12px;"))
        
        self.val_v = QLabel("0.0 V")
        self.val_v.setStyleSheet("font-size: 38px; font-weight: bold; padding: 5px 0;")
        layout.addWidget(self.val_v)

        self.val_delta = QLabel("ΔV: 0.000 V")
        self.val_delta.setStyleSheet("font-size: 18px; color: #00FF7F;")
        layout.addWidget(self.val_delta)

        # Ligne Min/Max
        mm_layout = QHBoxLayout()
        self.val_min = QLabel("MIN: 0.00V")
        self.val_max = QLabel("MAX: 0.00V")
        self.val_min.setStyleSheet("color: #888888; font-size: 13px;")
        self.val_max.setStyleSheet("color: #888888; font-size: 13px;")
        mm_layout.addWidget(self.val_min)
        mm_layout.addWidget(self.val_max)
        layout.addLayout(mm_layout)

        layout.addStretch()
        layout.addWidget(QLabel("TOUCH FOR DETAILS", alignment=Qt.AlignCenter, styleSheet="color: #444444; font-size: 10px;"))

    def mousePressEvent(self, event): self.clicked.emit()

    def update_data(self, v_total, delta, v_min, v_max):
        self.val_v.setText(f"{v_total:.1f} V")
        self.val_delta.setText(f"ΔV: {delta:.3f} V")
        self.val_min.setText(f"MIN: {v_min:.2f}V")
        self.val_max.setText(f"MAX: {v_max:.2f}V")
        color = "#FF3232" if delta > 0.050 else "#00FF7F"
        self.val_delta.setStyleSheet(f"font-size: 18px; color: {color};")

# --- L'ICÔNE DE PILE (Détail des 16 cellules) ---
class BatteryIcon(QWidget):
    def __init__(self, cell_id, parent=None):
        super().__init__(parent)
        self.voltage = 3.6
        self.cell_id = cell_id
        self.setFixedSize(65, 100)

    def set_voltage(self, v):
        self.voltage = v
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessin de la pile (Corps)
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.drawRoundedRect(18, 10, 28, 65, 4, 4)
        
        # Remplissage dynamique
        ratio = max(0, min(1, (self.voltage - 2.8) / 1.4))
        color = QColor(0, 255, 127) if self.voltage > 3.2 else QColor(255, 50, 50)
        painter.setBrush(color)
        h = int(ratio * 61)
        painter.drawRect(20, 75 - h, 24, h)
        
        # Texte Cell ID et Voltage
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Orbitron", 8))
        painter.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, f"{self.voltage:.2f}V")
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(QRect(0, 0, self.width(), 10), Qt.AlignTop | Qt.AlignHCenter, f"#{self.cell_id}")

# --- BARRE SOC (Main Page) ---
class PackBatteryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc = 0
        self.setFixedSize(220, 100)

    def update_status(self, soc):
        self.soc = int(soc)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Barre horizontale
        w, h = 180, 10
        x, y = (self.width()-w)//2, 10
        painter.setBrush(QColor(30, 30, 30))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRoundedRect(x, y, w, h, 5, 5)
        
        fill = int((self.soc/100)*w)
        if fill > 0:
            painter.setBrush(QColor(0, 255, 127))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, fill, h, 5, 5)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Orbitron", 36, QFont.Weight.Bold))
        painter.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, f"{self.soc}%")