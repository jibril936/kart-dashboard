from __future__ import annotations

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.components.kart_top_view_widget import KartTopViewWidget


class CenterPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._steering_angle_deg = 0.0
        self._drive_mode: str | None = None
        self._control_mode: str | None = None
        self._charging: bool | None = None
        self._has_steering = False
        self._compact = False
        self._ui_scale = 1.0

        self.setMinimumSize(420, 280)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(8)

        self.kart_widget = KartTopViewWidget()

        self.angle_label = QLabel("+0.0°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.angle_label.setStyleSheet("color: #a8f3ff; letter-spacing: 1px;")
        self.angle_label.setFont(QFont("Bahnschrift", 15, QFont.Weight.DemiBold))

        root.addWidget(self.kart_widget, 1)
        root.addWidget(self.angle_label)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self.angle_label.setFont(QFont("Bahnschrift", max(11, int((13 if compact else 15) * ui_scale)), QFont.Weight.DemiBold))

    def set_state(
        self,
        steering_angle_deg: float | None,
        drive_mode: str | None = None,
        control_mode: str | None = None,
        charging_state: bool | None = None,
        gear: str | None = None,
    ) -> None:
        _ = gear
        clamped = 0.0 if steering_angle_deg is None else max(-30.0, min(30.0, steering_angle_deg))
        self._steering_angle_deg = clamped
        self._drive_mode = drive_mode
        self._control_mode = control_mode
        self._charging = charging_state
        self._has_steering = steering_angle_deg is not None

        if self._has_steering:
            self.angle_label.setText(f"∡ {clamped:+.1f}°")
        else:
            self.angle_label.setText("∡ --.-°")

        self.kart_widget.set_steer_angle(steering_angle_deg)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(8.0, 8.0, -8.0, -8.0)
        painter.setPen(QPen(QColor("#273547"), 1.0))

        panel_grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        panel_grad.setColorAt(0.0, QColor("#111c2c"))
        panel_grad.setColorAt(0.55, QColor("#0a131f"))
        panel_grad.setColorAt(1.0, QColor("#04080e"))
        painter.setBrush(panel_grad)
        painter.drawRoundedRect(rect, 20, 20)

        painter.setPen(QPen(QColor("#41596e"), 2.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 16, 16)

        painter.setPen(QPen(QColor(84, 233, 255, 90), 1.4))
        painter.drawLine(QLineF(rect.left() + 14.0, rect.top() + 12.0, rect.right() - 18.0, rect.top() + 12.0))
        painter.drawLine(QLineF(rect.left() + 18.0, rect.bottom() - 12.0, rect.right() - 14.0, rect.bottom() - 12.0))
