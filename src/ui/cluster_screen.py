from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components.bottom_bar import BottomBarStrip
from src.ui.components.center_panel import CenterPanel

SPEED_MIN_KMH = 0
SPEED_MAX_KMH = 60
POWER_MIN_KW = -12.0
POWER_MAX_KW = 12.0


class SegmentedGauge(QWidget):
    def __init__(
        self,
        title: str,
        unit: str,
        minimum: float,
        maximum: float,
        segments: int = 36,
        value_font_size: int = 66,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = float(minimum)
        self._max = float(maximum)
        self._segments = max(30, min(40, int(segments)))
        self._value = self._min
        self._display_value = self._min
        self._unit = unit
        self._value_font_size = value_font_size

        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumSize(280, 360)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        self.title_label.setStyleSheet("color: #6D7A85; letter-spacing: 3px; background: transparent; border: none;")

        self.unit_label = QLabel(unit)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setFont(QFont("Inter", 14, QFont.Weight.Medium))
        self.unit_label.setStyleSheet("color: #7B8791; background: transparent; border: none;")

        root.addWidget(self.title_label)
        root.addStretch(1)
        root.addWidget(self.unit_label)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(28)
        glow.setOffset(0, 0)
        glow.setColor(QColor("#00FFFF"))
        self.setGraphicsEffect(glow)

        self._anim = QPropertyAnimation(self, b"displayValue", self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_value(self, value: float) -> None:
        self._value = max(self._min, min(self._max, float(value)))
        self._anim.stop()
        self._anim.setStartValue(self._display_value)
        self._anim.setEndValue(self._value)
        self._anim.start()

    @pyqtProperty(float)
    def displayValue(self) -> float:  # noqa: N802
        return self._display_value

    @displayValue.setter
    def displayValue(self, value: float) -> None:  # noqa: N802
        self._display_value = float(value)
        self.update()

    def _formatted_value(self) -> str:
        if self._unit == "km/h":
            return f"{int(round(self._display_value))}"
        return f"{self._display_value:+.1f}"

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        radius = min(w, h) * 0.34
        center_x = w / 2
        center_y = h / 2 + 6

        ratio = 0.0 if self._max == self._min else (self._display_value - self._min) / (self._max - self._min)
        active_segments = int(max(0.0, min(1.0, ratio)) * self._segments)

        start_angle = -220.0
        sweep = 260.0
        angle_step = sweep / max(1, self._segments - 1)

        for index in range(self._segments):
            angle = start_angle + (index * angle_step)

            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(angle)
            painter.translate(radius, 0)

            if index < active_segments:
                painter.setBrush(QColor("#00FFFF"))
            else:
                painter.setBrush(QColor("#1B232A"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(-2, -14, 4, 24)
            painter.restore()

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Inter", self._value_font_size, QFont.Weight.Bold))
        painter.drawText(self.rect().adjusted(0, -18, 0, 0), Qt.AlignmentFlag.AlignCenter, self._formatted_value())


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, ui_scale: float = 1.0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_ui_scale = ui_scale

        self.setObjectName("ClusterScreen")
        self.setWindowTitle("KART DASHBOARD PRO V2 - ACTIVE")
        self.setStyleSheet(
            "#ClusterScreen { background-color: #050505; border: none; }"
            " QWidget { border: none; background: transparent; }"
        )

        grid = QGridLayout(self)
        grid.setContentsMargins(42, 28, 42, 24)
        grid.setSpacing(30)

        self.speed_gauge = SegmentedGauge("SPEED", "km/h", SPEED_MIN_KMH, SPEED_MAX_KMH, segments=38, value_font_size=72)
        self.center_panel = CenterPanel()
        self.power_gauge = SegmentedGauge("POWER", "kW", POWER_MIN_KW, POWER_MAX_KW, segments=34, value_font_size=64)

        self.bottom_bar = BottomBarStrip()
        self.bottom_bar.tech_button.clicked.connect(self.tech_requested.emit)

        grid.addWidget(self.speed_gauge, 0, 0)
        grid.addWidget(self.center_panel, 0, 1)
        grid.addWidget(self.power_gauge, 0, 2)
        grid.addWidget(self.bottom_bar, 1, 0, 1, 3)

        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 0)

    def render(self, state: VehicleTechState) -> None:
        speed = state.speed_kmh
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        motor_temp = state.motor_temp_C

        if speed is not None:
            self.speed_gauge.set_value(float(speed))

        drive_mode = getattr(state, "drive_mode", None)
        control_mode = getattr(state, "control_mode", None)

        self.center_panel.set_state(
            float(steering_angle) if steering_angle is not None else None,
            drive_mode=drive_mode,
            control_mode=control_mode,
            charging_state=charging,
            gear=None,
        )

        battery_current = state.battery_charge_current_A
        if battery_v is not None and battery_current is not None:
            self.power_gauge.set_value((float(battery_v) * float(battery_current)) / 1000.0)

        self.bottom_bar.set_values(
            battery_voltage=battery_v,
            battery_soc_percent=None,
            motor_temp_c=motor_temp,
        )
