from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

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

        self.setMinimumSize(320, 280)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 10)
        root.setSpacing(8)

        header = QWidget()
        self.header_layout = QGridLayout(header)
        self.header_layout.setContentsMargins(10, 8, 10, 8)
        self.header_layout.setHorizontalSpacing(14)
        self.header_layout.setVerticalSpacing(2)

        self.drive_mode_label = QLabel("DRIVE MODE")
        self.drive_mode_label.setStyleSheet("color: #89a1bc;")
        self.drive_mode_label.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))

        self.drive_mode_value = QLabel("MODE N/A")
        self.drive_mode_value.setStyleSheet("color: #eff6ff;")
        self.drive_mode_value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        self.control_mode_label = QLabel("CONTROL")
        self.control_mode_label.setStyleSheet("color: #89a1bc;")
        self.control_mode_label.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))

        self.control_mode_value = QLabel("CONTROL N/A")
        self.control_mode_value.setStyleSheet("color: #eff6ff;")
        self.control_mode_value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        self.charge_status = QLabel("READY")
        self.charge_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.charge_status.setStyleSheet("color: #88a2bf;")
        self.charge_status.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))

        self.header_layout.addWidget(self.drive_mode_label, 0, 0)
        self.header_layout.addWidget(self.control_mode_label, 0, 1)
        self.header_layout.addWidget(self.charge_status, 0, 2, 2, 1)
        self.header_layout.addWidget(self.drive_mode_value, 1, 0)
        self.header_layout.addWidget(self.control_mode_value, 1, 1)

        header.setStyleSheet("background: rgba(20, 30, 45, 165); border: 1px solid #2a3b52; border-radius: 9px;")

        self.kart_widget = KartTopViewWidget()

        self.angle_label = QLabel("+0.0°")
        self.angle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.angle_label.setStyleSheet("color: #c7d8eb;")
        self.angle_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Medium))

        root.addWidget(header)
        root.addWidget(self.kart_widget, 1)
        root.addWidget(self.angle_label)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        base = 6 if compact else 8
        self.header_layout.setHorizontalSpacing(int((10 if compact else 14) * ui_scale))
        self.header_layout.setContentsMargins(int((8 if compact else 10) * ui_scale), int(base * ui_scale), int((8 if compact else 10) * ui_scale), int(base * ui_scale))

        self.drive_mode_label.setFont(QFont("Segoe UI", max(7, int((7 if compact else 8) * ui_scale)), QFont.Weight.DemiBold))
        self.control_mode_label.setFont(QFont("Segoe UI", max(7, int((7 if compact else 8) * ui_scale)), QFont.Weight.DemiBold))
        self.charge_status.setFont(QFont("Segoe UI", max(7, int((7 if compact else 8) * ui_scale)), QFont.Weight.DemiBold))
        self.drive_mode_value.setFont(QFont("Segoe UI", max(8, int((9 if compact else 10) * ui_scale)), QFont.Weight.Bold))
        self.control_mode_value.setFont(QFont("Segoe UI", max(8, int((9 if compact else 10) * ui_scale)), QFont.Weight.Bold))
        self.angle_label.setFont(QFont("Segoe UI", max(11, int((13 if compact else 15) * ui_scale)), QFont.Weight.Medium))

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

        self.drive_mode_value.setText((drive_mode or "MODE N/A").upper())
        self.control_mode_value.setText((control_mode or "CONTROL N/A").upper())

        if charging_state:
            self.charge_status.setText("⚡ CHARGING")
            self.charge_status.setStyleSheet("color: #ffd36f;")
        else:
            self.charge_status.setText("READY")
            self.charge_status.setStyleSheet("color: #88a2bf;")

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

        rect = QRectF(self.rect()).adjusted(8.0, 8.0, -8.0, -8.0)
        painter.setPen(QPen(QColor("#273547"), 1.0))

        panel_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        panel_grad.setColorAt(0.0, QColor("#0f1624"))
        panel_grad.setColorAt(0.6, QColor("#0c1420"))
        panel_grad.setColorAt(1.0, QColor("#09111a"))
        painter.setBrush(panel_grad)
        painter.drawRoundedRect(rect, 20, 20)

        if not self._compact:
            header_rect = rect.adjusted(20, 12, -20, -rect.height() + 58)
            painter.setPen(QPen(QColor("#30445c"), 1.0))
            header_grad = QLinearGradient(header_rect.topLeft(), header_rect.bottomLeft())
            header_grad.setColorAt(0.0, QColor("#131f2f"))
            header_grad.setColorAt(1.0, QColor("#111b2a"))
            painter.setBrush(header_grad)
            painter.drawRoundedRect(header_rect, 10, 10)
