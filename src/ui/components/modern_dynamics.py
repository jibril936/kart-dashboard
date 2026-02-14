from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget


class ModernDynamics(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode = "SPORT"
        self._amps = 0.0
        self._brake_on = False
        self._distance_cm = 400.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(170, 260)

    def set_mode(self, mode: str) -> None:
        self._mode = (mode or "SPORT").upper()
        self.update()

    def set_current(self, amps: float) -> None:
        self._amps = max(-200.0, min(200.0, float(amps)))
        self.update()

    def set_brake_state(self, active: bool) -> None:
        self._brake_on = bool(active)
        self.update()

    def update_radars(self, distances: list[float]) -> None:
        if distances:
            self._distance_cm = max(0.0, min(400.0, min(float(v) for v in distances)))
            self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())

        p.setPen(QColor("#4DF3FF"))
        p.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        p.drawText(QRectF(0.0, 10.0, w, 30.0), Qt.AlignmentFlag.AlignHCenter, self._mode)

        bar_rect = QRectF(w * 0.45, h * 0.18, w * 0.1, h * 0.52)
        p.setPen(QPen(QColor("#243142"), 1.4))
        p.setBrush(QColor("#0F1724"))
        p.drawRoundedRect(bar_rect, 5.0, 5.0)

        amps_ratio = abs(self._amps) / 200.0
        fill_h = (bar_rect.height() - 4.0) * amps_ratio
        fill_rect = QRectF(bar_rect.left() + 2.0, bar_rect.bottom() - 2.0 - fill_h, bar_rect.width() - 4.0, fill_h)
        fill_color = QColor("#60D7FF") if self._amps < 0 else QColor("#00E5A8")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill_color)
        p.drawRoundedRect(fill_rect, 3.0, 3.0)

        p.setPen(QColor("#90A1BA"))
        p.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        p.drawText(QRectF(0.0, bar_rect.bottom() + 8.0, w, 20.0), Qt.AlignmentFlag.AlignHCenter, f"{self._amps:+.0f} A")

        symbol_rect = QRectF(w * 0.25, h * 0.78, w * 0.5, h * 0.16)
        symbol_color = QColor("#FF4141") if self._brake_on else QColor("#2A2F3B")
        p.setPen(symbol_color)
        p.setFont(QFont("Inter", 26, QFont.Weight.Black))
        p.drawText(symbol_rect, Qt.AlignmentFlag.AlignCenter, "!")

        if self._distance_cm < 50.0:
            center_x = w * 0.5
            center_y = h * 0.86
            p.setPen(QPen(QColor("#FF3C3C"), 2.0))
            for radius in (18.0, 28.0, 38.0):
                arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2.0, radius * 2.0)
                path = QPainterPath()
                path.arcMoveTo(arc_rect, 25)
                path.arcTo(arc_rect, 25, 130)
                p.drawPath(path)
