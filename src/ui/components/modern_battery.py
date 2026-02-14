from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class ModernBattery(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage = 52.0
        self._show_percent = True
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(170, 260)

    def set_voltage(self, voltage: float) -> None:
        self._voltage = max(44.0, min(54.0, float(voltage)))
        self.update()

    def set_show_percent(self, enabled: bool) -> None:
        self._show_percent = bool(enabled)
        self.update()

    def _charge_ratio(self) -> float:
        return (self._voltage - 44.0) / 10.0

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())

        battery_w = min(78.0, w * 0.46)
        battery_h = h * 0.78
        body_x = 18.0
        body_y = (h - battery_h) * 0.52

        body = QRectF(body_x, body_y + 12.0, battery_w, battery_h - 12.0)
        cap_w = battery_w * 0.38
        cap_h = 10.0
        cap = QRectF(body.center().x() - cap_w / 2.0, body_y, cap_w, cap_h)

        p.setPen(QPen(QColor("#5B6578"), 2.2))
        p.setBrush(QColor("#101822"))
        p.drawRoundedRect(body, 8.0, 8.0)
        p.drawRoundedRect(cap, 3.0, 3.0)

        segments = 10
        margin = 6.0
        spacing = 4.0
        seg_h = (body.height() - (margin * 2.0) - spacing * (segments - 1)) / segments
        seg_w = body.width() - margin * 2.0

        active_segments = int(round(self._charge_ratio() * segments))
        active_segments = max(0, min(segments, active_segments))

        for i in range(segments):
            y = body.bottom() - margin - (i + 1) * seg_h - i * spacing
            rect = QRectF(body.left() + margin, y, seg_w, seg_h)
            if i < active_segments:
                ratio = (i + 1) / segments
                if ratio > 0.7:
                    color = QColor("#3CFF8D")
                elif ratio > 0.35:
                    color = QColor("#FFD34D")
                else:
                    color = QColor("#FF4D4D")
            else:
                color = QColor("#243142")
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect, 2.0, 2.0)

        ratio = self._charge_ratio()
        percent = int(round(ratio * 100.0))
        display = f"{percent}%" if self._show_percent else f"{self._voltage:.1f}V"

        text_x = body.right() + 18.0
        text_rect = QRectF(text_x, body_y + 22.0, max(60.0, w - text_x - 8.0), 96.0)

        p.setPen(QColor("#F3F7FF"))
        font = QFont("Inter", 26, QFont.Weight.Black)
        p.setFont(font)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display)

        subtitle = "BATTERY"
        p.setPen(QColor("#6E7E98"))
        p.setFont(QFont("Inter", 11, QFont.Weight.DemiBold))
        p.drawText(
            QRectF(text_x, text_rect.bottom() - 4.0, text_rect.width(), 22.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            subtitle,
        )
