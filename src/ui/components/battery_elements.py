from __future__ import annotations

from qtpy.QtCore import Qt, QRect, Signal
from qtpy.QtGui import QColor, QFont, QPainter, QPen
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class CircularBatteryWidget(QWidget):
    """
    Widget SOC circulaire (utilisé par ClusterPage).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self._soc = 0

    def update_status(self, soc: int) -> None:
        self._soc = max(0, min(100, int(soc)))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()

        # Anneau fond
        p.setPen(QPen(QColor(30, 30, 30), 14))
        p.drawArc(20, 20, 180, 180, 0, 360 * 16)

        # Couleur dynamique
        if self._soc <= 15:
            color = QColor(255, 40, 40)
        elif self._soc <= 35:
            color = QColor(255, 140, 0)
        else:
            color = QColor(0, 255, 150)

        # Anneau progress (départ en haut)
        p.setPen(QPen(color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        span = int((self._soc / 100.0) * 360.0 * 16)
        p.drawArc(20, 20, 180, 180, 90 * 16, -span)

        # Texte
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 48, QFont.Weight.Bold))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._soc}%")

        # Label discret
        p.setPen(QColor(140, 140, 140))
        p.setFont(QFont("Orbitron", 10))
        p.drawText(QRect(0, cy + 45, rect.width(), 20), Qt.AlignmentFlag.AlignCenter, "SOC")


class BMSSummaryCard(QFrame):
    """
    Carte "BMS HEALTH" cliquable.
    Affiche Vpack + stats cellules.
    """
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(320, 240)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "QFrame { background-color: #0A0A0A; border: 1px solid #222; border-radius: 16px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("BMS HEALTH")
        title.setStyleSheet("color: cyan; font-size: 11px; border:none; font-family:'Orbitron';")
        layout.addWidget(title)

        self.lbl_vpack = QLabel("0.0 V")
        self.lbl_vpack.setStyleSheet(
            "color: white; font-size: 40px; font-weight: bold; border:none; font-family:'Orbitron';"
        )
        layout.addWidget(self.lbl_vpack)

        self.lbl_delta = QLabel("ΔV: 0.000 V")
        self.lbl_delta.setStyleSheet("color: #00FF7F; font-size: 16px; border:none; font-family:'Orbitron';")
        layout.addWidget(self.lbl_delta)

        self.min_bar = self._add_bar(layout, "MIN")
        self.max_bar = self._add_bar(layout, "MAX")

        hint = QLabel("Tap to open FULL BMS CONTROL")
        hint.setStyleSheet("color:#444; font-size:10px; border:none; font-family:'Orbitron';")
        layout.addWidget(hint)

        layout.addStretch(1)

    def _add_bar(self, layout, name: str):
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(name)
        lbl.setStyleSheet("color:#666; font-size:9px; border:none; font-family:'Orbitron';")

        bar = QProgressBar()
        bar.setFixedHeight(6)
        bar.setTextVisible(False)
        bar.setRange(0, 100)
        bar.setStyleSheet(
            "QProgressBar { background:#111; border:none; border-radius:3px; } "
            "QProgressBar::chunk { background:cyan; border-radius:3px; }"
        )

        val = QLabel("0.00V")
        val.setStyleSheet("color:white; font-size:11px; border:none; font-family:'Orbitron';")

        row.addWidget(lbl)
        row.addWidget(bar, 1)
        row.addWidget(val)

        layout.addLayout(row)
        return (bar, val)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def update_data(self, vpack: float, delta: float, v_min: float, v_max: float) -> None:
        self.lbl_vpack.setText(f"{vpack:.1f} V")
        self.lbl_delta.setText(f"ΔV: {delta:.3f} V")

        # Échelle cellules (2.50 .. 3.65)
        v_lo, v_hi = 2.50, 3.65
        span = max(1e-6, (v_hi - v_lo))

        for bar, label, val in [
            (self.min_bar[0], self.min_bar[1], v_min),
            (self.max_bar[0], self.max_bar[1], v_max),
        ]:
            pct = int(max(0.0, min(1.0, (val - v_lo) / span)) * 100.0)
            bar.setValue(pct)
            label.setText(f"{val:.2f}V")


class BatteryIcon(QWidget):
    """
    BatteryIcon cellule (Overlay)
      - Taille: 45x85
      - Tension: 2.50V (0%) -> 3.65V (100%)
      - Couleurs:
          Rouge  : V<3.0V ou V>3.6V
          Orange : 3.0V-3.2V
          Vert   : 3.2V-3.45V
          Bleu   : >3.45V
    """

    V_MIN = 2.50
    V_MAX = 3.65

    def __init__(self, cell_id: int, parent=None):
        super().__init__(parent)
        self.cell_id = int(cell_id)
        self.voltage = 3.60
        self.setFixedSize(45, 85)

    def set_voltage(self, v: float) -> None:
        self.voltage = float(v)
        self.update()

    def _color_for_voltage(self, v: float) -> QColor:
        if v < 3.0 or v > 3.6:
            return QColor(255, 40, 40)    # Rouge critique
        if v < 3.2:
            return QColor(255, 140, 0)    # Orange
        if v <= 3.45:
            return QColor(0, 255, 150)    # Vert nominal
        return QColor(60, 160, 255)       # Bleu charge

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Body geometry
        body_x = 12
        body_y = 10
        body_w = w - 24
        body_h = 54

        cap_w = 10
        cap_h = 7
        cap_x = (w - cap_w) // 2
        cap_y = body_y - 6

        # Outline
        p.setPen(QPen(QColor(90, 90, 90), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(body_x, body_y, body_w, body_h, 3, 3)
        p.drawRoundedRect(cap_x, cap_y, cap_w, cap_h, 2, 2)

        v = self.voltage
        ratio = (v - self.V_MIN) / (self.V_MAX - self.V_MIN)
        ratio = max(0.0, min(1.0, ratio))

        fill_color = self._color_for_voltage(v)

        # Fill
        inner_pad = 2
        inner_h = body_h - 2 * inner_pad
        fill_h = int(inner_h * ratio)

        fill_x = body_x + inner_pad
        fill_y = body_y + inner_pad + (inner_h - fill_h)
        fill_w = body_w - 2 * inner_pad

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill_color)
        if fill_h > 0:
            p.drawRoundedRect(fill_x, fill_y, fill_w, fill_h, 2, 2)

        # Text
        p.setPen(QColor(160, 160, 160))
        p.setFont(QFont("Orbitron", 7))
        p.drawText(QRect(0, 0, w, 18), Qt.AlignmentFlag.AlignCenter, f"#{self.cell_id}")

        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 8, QFont.Weight.Bold))
        p.drawText(QRect(0, h - 24, w, 24), Qt.AlignmentFlag.AlignCenter, f"{v:.2f}V")
