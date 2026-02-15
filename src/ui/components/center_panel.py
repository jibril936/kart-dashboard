from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.components.kart_top_view_widget import KartTopViewWidget


class CenterPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._compact = False

        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 8, 30, 8)
        root.setSpacing(10)

        self.kart_widget = KartTopViewWidget()
        self.kart_widget.setMinimumHeight(260)

        self.angle_label = QLabel("STEER +0.0°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.angle_label.setStyleSheet("color: #A4B9C8; letter-spacing: 3px; border: none; background: transparent;")
        self.angle_label.setFont(QFont("Inter", 14, QFont.Weight.Medium))

        root.addWidget(self.kart_widget, 1)
        root.addWidget(self.angle_label)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        size = max(11, int((12 if compact else 14) * ui_scale))
        self.angle_label.setFont(QFont("Inter", size, QFont.Weight.Medium))

    def set_state(
        self,
        steering_angle_deg: float | None,
        drive_mode: str | None = None,
        control_mode: str | None = None,
        charging_state: bool | None = None,
        gear: str | None = None,
    ) -> None:
        _ = (drive_mode, control_mode, charging_state, gear)
        if steering_angle_deg is None:
            self.angle_label.setText("STEER --.-°")
        else:
            clamped = max(-30.0, min(30.0, float(steering_angle_deg)))
            self.angle_label.setText(f"STEER {clamped:+.1f}°")
        self.kart_widget.set_steer_angle(steering_angle_deg)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
