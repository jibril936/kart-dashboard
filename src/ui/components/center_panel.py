from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.components.kart_top_view_widget import KartTopViewWidget


class CenterPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._compact = False

        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self.kart_widget = KartTopViewWidget()
        self.kart_widget.setMinimumSize(320, 220)

        self.angle_label = QLabel("STEER +0.0°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.angle_label.setFont(QFont("Roboto Mono", 13, QFont.Weight.DemiBold))
        self.angle_label.setStyleSheet(
            """
            color: #CFE7F7;
            letter-spacing: 1px;
            padding: 6px 14px;
            background-color: rgba(8, 20, 28, 0.85);
            border: 1px solid #1E3A4A;
            border-radius: 14px;
            """
        )

        root.addWidget(self.kart_widget, 1)
        root.addWidget(self.angle_label)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        size = max(10, int((11 if compact else 13) * ui_scale))
        self.angle_label.setFont(QFont("Roboto Mono", size, QFont.Weight.DemiBold))

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
