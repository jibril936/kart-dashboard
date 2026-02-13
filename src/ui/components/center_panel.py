from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.components.kart_top_view_widget import KartTopViewWidget


class CenterPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._steering_angle_deg = 0.0
        self._mode: str | None = None
        self._has_steering = False

        self.setMinimumSize(320, 280)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(10)

        self.mode_label = QLabel("DRIVE MODE")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.mode_label.setStyleSheet("color: #8ca5bf;")
        self.mode_label.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))

        self.mode_value = QLabel("READY")
        self.mode_value.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.mode_value.setStyleSheet("color: #e0ebf8;")
        self.mode_value.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        self.kart_widget = KartTopViewWidget()

        self.angle_label = QLabel("+0.0°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.angle_label.setStyleSheet("color: #c7d8eb;")
        self.angle_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))

        root.addWidget(self.mode_label)
        root.addWidget(self.mode_value)
        root.addWidget(self.kart_widget, 1)
        root.addWidget(self.angle_label)

    def set_state(self, steering_angle_deg: float | None, mode: str | None = None, gear: str | None = None) -> None:
        _ = gear
        clamped = 0.0 if steering_angle_deg is None else max(-30.0, min(30.0, steering_angle_deg))
        self._steering_angle_deg = clamped
        self._mode = mode
        self._has_steering = steering_angle_deg is not None

        if mode:
            self.mode_value.setText(mode)
        else:
            self.mode_value.setText("READY")

        if self._has_steering:
            self.angle_label.setText(f"{clamped:+.1f}°")
        else:
            self.angle_label.setText("--.-°")

        self.kart_widget.set_steer_angle(steering_angle_deg)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(QPen(QColor("#273547"), 1.0))

        panel_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        panel_grad.setColorAt(0.0, QColor("#0f1624"))
        panel_grad.setColorAt(0.6, QColor("#0c1420"))
        panel_grad.setColorAt(1.0, QColor("#09111a"))
        painter.setBrush(panel_grad)
        painter.drawRoundedRect(rect, 20, 20)

        header_rect = rect.adjusted(20, 12, -20, -rect.height() + 58)
        painter.setPen(QPen(QColor("#30445c"), 1.0))
        header_grad = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
        header_grad.setColorAt(0.0, QColor("#131f2f"))
        header_grad.setColorAt(1.0, QColor("#111b2a"))
        painter.setBrush(header_grad)
        painter.drawRoundedRect(header_rect, 10, 10)
