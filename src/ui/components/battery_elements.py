from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QProgressBar
from qtpy.QtGui import QPainter, QColor, QPen, QFont
from qtpy.QtCore import Qt, QRect, Signal

# --- 1. LE CERCLE D'ÉNERGIE (Pour la Page 1 / Cluster) ---
class CircularBatteryWidget(QWidget):
    """Jauge circulaire centrale pour le SOC."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.soc = 0

    def update_status(self, soc):
        self.soc = int(soc)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Anneau de fond (Gris sombre)
        p.setPen(QPen(QColor(30, 30, 30), 12))
        p.drawArc(20, 20, 160, 160, 0 * 16, 360 * 16)
        
        # Anneau de progression (Couleur dynamique)
        if self.soc > 50: color = QColor(0, 255, 150)
        elif self.soc > 20: color = QColor(255, 165, 0)
        else: color = QColor(255, 50, 50)
        
        p.setPen(QPen(color, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        # On part du haut (90°) et on tourne selon le SOC
        # Span doit être négatif pour tourner dans le sens horaire
        span = int((self.soc / 100.0) * 360 * 16)
        p.drawArc(20, 20, 160, 160, 90 * 16, -span)
        
        # Texte central %
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 42, QFont.Weight.Bold))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.soc}%")

# --- 2. LE RÉSUMÉ BMS (Pour la Page 2 / Expert) ---
class BMSSummaryCard(QFrame):
    """Résumé 1/4 de page avec barres Min/Max."""
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 240)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame { background-color: #0A0A0A; border: 1px solid #222; border-radius: 15px; }
            QLabel { border: none; color: white; font-family: 'Orbitron'; }
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("BMS HEALTH", styleSheet="color: #00FFFF; font-weight: bold; font-size: 11px;"))
        
        self.val_v = QLabel("0.0 V")
        self.val_v.setStyleSheet("font-size: 38px; font-weight: bold; padding: 5px 0;")
        layout.addWidget(self.val_v)

        self.val_delta = QLabel("ΔV: 0.000 V")
        self.val_delta.setStyleSheet("font-size: 16px; color: #00FF7F;")
        layout.addWidget(self.val_delta)

        self.min_bar = self._create_row("MIN")
        self.max_bar = self._create_row("MAX")
        layout.addLayout(self.min_bar['layout'])
        layout.addLayout(self.max_bar['layout'])
        layout.addStretch()
        layout.addWidget(QLabel("TAP FOR DETAILS", alignment=Qt.AlignmentFlag.AlignCenter, styleSheet="color: #333; font-size: 9px;"))

    def _create_row(self, label):
        row = QHBoxLayout()
        l = QLabel(label); l.setStyleSheet("color: #666; font-size: 10px;")
        v = QLabel("0.00V"); v.setStyleSheet("font-weight: bold; font-size: 12px;")
        b = QProgressBar(); b.setFixedHeight(4); b.setTextVisible(False)
        b.setStyleSheet("QProgressBar { background: #222; border: none; } QProgressBar::chunk { background: #00FFFF; }")
        row.addWidget(l); row.addWidget(b); row.addWidget(v)
        return {'layout': row, 'bar': b, 'val': v}

    def mousePressEvent(self, event): self.clicked.emit()

    def update_data(self, v, delta, v_min, v_max):
        self.val_v.setText(f"{v:.1f} V")
        self.val_delta.setText(f"ΔV: {delta:.3f} V")
        for d, val in [(self.min_bar, v_min), (self.max_bar, v_max)]:
            p = int(((val - 2.8) / 1.4) * 100)
            d['bar'].setValue(max(0, min(100, p)))
            d['val'].setText(f"{val:.2f}V")

# --- 3. L'ICÔNE CELLULE COMPACTE (Pour l'Overlay) ---
class BatteryIcon(QWidget):
    """Icône réduite pour que 8 piles tiennent sur 800px."""
    def __init__(self, cell_id, parent=None):
        super().__init__(parent)
        self.voltage = 3.6
        self.cell_id = cell_id
        self.setFixedSize(65, 100)

    def set_voltage(self, v): self.voltage = v; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(60, 60, 60), 2))
        p.setBrush(QColor(20, 20, 20))
        p.drawRoundedRect(18, 15, 28, 60, 4, 4)
        
        ratio = max(0, min(1, (self.voltage - 2.8) / 1.4))
        color = QColor(0, 255, 150) if self.voltage > 3.2 else QColor(255, 50, 50)
        p.setBrush(color); p.setPen(Qt.PenStyle.NoPen)
        h = int(ratio * 56)
        p.drawRect(20, 17 + (56 - h), 24, h)

        p.setPen(QColor(255, 255, 255)); p.setFont(QFont("Orbitron", 8))
        p.drawText(QRect(0, 78, 65, 20), Qt.AlignmentFlag.AlignCenter, f"{self.voltage:.2f}V")