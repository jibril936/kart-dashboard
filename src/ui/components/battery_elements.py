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
        cy = rect.center().y()

        p.setPen(QPen(QColor(30, 30, 30), 14))
        p.drawArc(20, 20, 180, 180, 0, 360 * 16)

        if self._soc <= 15:
            color = QColor(255, 40, 40)
        elif self._soc <= 35:
            color = QColor(255, 140, 0)
        else:
            color = QColor(0, 255, 150)

        p.setPen(QPen(color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        span = int((self._soc / 100.0) * 360.0 * 16)
        p.drawArc(20, 20, 180, 180, 90 * 16, -span)

        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Orbitron", 48, QFont.Weight.Bold))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self._soc}%")

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
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)

        title = QLabel("BMS HEALTH")
        title.setObjectName("CardTitle")
        layout.addWidget(title)

        self.lbl_vpack = QLabel("0.0 V")
        self.lbl_vpack.setObjectName("ValueBig")
        self.lbl_vpack.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(self.lbl_vpack)

        self.lbl_delta = QLabel("ΔV: 0.000 V")
        self.lbl_delta.setObjectName("ValueGood")
        self.lbl_delta.setStyleSheet("font-size: 12px; font-weight: 700;")
        layout.addWidget(self.lbl_delta)

        self.min_bar = self._add_bar(layout, "MIN")
        self.max_bar = self._add_bar(layout, "MAX")

        hint = QLabel("Tap to open FULL BMS CONTROL")
        hint.setObjectName("Hint")
        hint.setStyleSheet("font-size: 10px;")
        layout.addWidget(hint)

        layout.addStretch(1)

    def _polish(self, w):
        w.style().unpolish(w)
        w.style().polish(w)
        w.update()

    def _set_delta_level(self, delta: float) -> None:
        if delta >= 0.150:
            name = "ValueBad"
        elif delta >= 0.080:
            name = "ValueWarn"
        else:
            name = "ValueGood"

        if self.lbl_delta.objectName() != name:
            self.lbl_delta.setObjectName(name)
            self._polish(self.lbl_delta)

    def _add_bar(self, layout: QVBoxLayout, name: str):
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(name)
        lbl.setObjectName("Muted")
        lbl.setStyleSheet("font-size: 10px;")

        bar = QProgressBar()
        bar.setFixedHeight(6)
        bar.setTextVisible(False)
        bar.setRange(0, 100)

        val = QLabel("0.00V")
        val.setObjectName("Value")
        val.setStyleSheet("font-size: 11px;")

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
        self._set_delta_level(delta)

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
    BatteryIcon cellule COMPACT (Overlay)

    - Hauteur ~58px max
    - Numéro cellule à GAUCHE de la barre
    - Barre plus basse
    - Voltage en dessous (petit)

    Tension: 2.50V -> 3.65V
    Couleurs:
    Rouge : V<3.0V ou V>3.6V
    Orange : 3.0V-3.2V
    Vert : 3.2V-3.45V
    Bleu : >3.45V
    """

    V_MIN = 2.50
    V_MAX = 3.65

    def __init__(self, cell_id: int, parent=None):
        super().__init__(parent)
        self.cell_id = int(cell_id)
        self.voltage = 3.60
        self.setFixedSize(96, 58)

    def set_voltage(self, v: float) -> None:
        self.voltage = float(v)
        self.update()

    def _color_for_voltage(self, v: float) -> QColor:
        if v < 3.0 or v > 3.6:
            return QColor(255, 40, 40)
        if v < 3.2:
            return QColor(255, 140, 0)
        if v <= 3.45:
            return QColor(0, 255, 150)
        return QColor(60, 160, 255)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        id_w = 24
        bar_x = id_w + 6
        bar_y = 12
        bar_w = w - bar_x - 8
        bar_h = 12

        v = self.voltage
        ratio = (v - self.V_MIN) / (self.V_MAX - self.V_MIN)
        ratio = max(0.0, min(1.0, ratio))
        fill_w = int((bar_w - 4) * ratio)

        p.setPen(QColor(170, 170, 170))
        p.setFont(QFont("Orbitron", 8, QFont.Weight.Bold))
        p.drawText(
            QRect(0, bar_y - 2, id_w + 2, bar_h + 4),
            Qt.AlignmentFlag.AlignCenter,
            f"#{self.cell_id}",
        )

        p.setPen(QPen(QColor(90, 90, 90), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._color_for_voltage(v))
        if fill_w > 0:
            p.drawRoundedRect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4, 3, 3)

        p.setPen(QColor(245, 245, 245))
        p.setFont(QFont("Orbitron", 8))
        p.drawText(
            QRect(0, h - 22, w, 20),
            Qt.AlignmentFlag.AlignCenter,
            f"{v:.2f}V",
        )