from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components.bottom_bar import BottomBarStrip
from src.ui.components.center_panel import CenterPanel

SPEED_MIN_KMH = 0
SPEED_MAX_KMH = 60
POWER_MIN_KW = -12.0
POWER_MAX_KW = 12.0


class SegmentsArc(QWidget):
    def __init__(self, segments: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._segments = segments
        self._active = 0
        self.setStyleSheet("background: transparent; border: none;")

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(26)
        glow.setOffset(0, 0)
        glow.setColor(QColor("#19C8FF"))
        self.setGraphicsEffect(glow)

    def set_active(self, value: int) -> None:
        self._active = max(0, min(self._segments, int(value)))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(10, 10, -10, -10)
        center = rect.center()
        radius = min(rect.width(), rect.height()) * 0.44

        start_angle = 215.0
        span = 290.0
        for index in range(self._segments):
            t = index / max(1, self._segments - 1)
            angle = math.radians(start_angle - t * span)

            cx = center.x() + radius * math.cos(angle)
            cy = center.y() - radius * math.sin(angle)

            painter.save()
            painter.translate(cx, cy)
            painter.rotate(-(start_angle - t * span) + 90)

            if index < self._active:
                painter.setBrush(QColor("#56D8FF"))
            else:
                painter.setBrush(QColor("#222222"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(-3.0, -11.0, 6.0, 16.0), 2.0, 2.0)
            painter.restore()


class SegmentedGauge(QWidget):
    def __init__(self, title: str, unit: str, minimum: float, maximum: float, segments: int, value_size: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._min = float(minimum)
        self._max = float(maximum)
        self._value = self._min
        self._display = self._min
        self._unit = unit
        self._segments = segments

        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumSize(280, 360)

        self._anim = QPropertyAnimation(self, b"displayValue", self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #66727B; letter-spacing: 3px; background: transparent; border: none;")
        self.title_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))

        self.arc = SegmentsArc(segments)

        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        self.value_label.setFont(QFont("Inter", value_size, QFont.Weight.Bold))

        self.unit_label = QLabel(unit)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setStyleSheet("color: #7B8791; background: transparent; border: none;")
        self.unit_label.setFont(QFont("Inter", 14, QFont.Weight.Medium))

        root.addWidget(self.title_label)
        root.addWidget(self.arc, 1)
        root.addWidget(self.value_label)
        root.addWidget(self.unit_label)

    def set_value(self, value: float) -> None:
        self._value = max(self._min, min(self._max, float(value)))
        self._anim.stop()
        self._anim.setStartValue(self._display)
        self._anim.setEndValue(self._value)
        self._anim.start()

    @pyqtProperty(float)
    def displayValue(self) -> float:  # noqa: N802
        return self._display

    @displayValue.setter
    def displayValue(self, value: float) -> None:  # noqa: N802
        self._display = float(value)
        ratio = 0.0 if self._max == self._min else (self._display - self._min) / (self._max - self._min)
        self.arc.set_active(round(max(0.0, min(1.0, ratio)) * self._segments))
        if self._unit == "km/h":
            self.value_label.setText(f"{int(round(self._display))}")
        else:
            self.value_label.setText(f"{self._display:+.1f}")

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, ui_scale: float = 1.0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_ui_scale = ui_scale

        self.setObjectName("ClusterScreen")
        self.setStyleSheet("#ClusterScreen { background: #050505; border: none; } QWidget { border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(44, 28, 44, 24)
        root.setSpacing(18)

        top_zone = QHBoxLayout()
        top_zone.setContentsMargins(0, 0, 0, 0)
        top_zone.setSpacing(30)

        self.speed_gauge = SegmentedGauge("SPEED", "km/h", SPEED_MIN_KMH, SPEED_MAX_KMH, segments=40, value_size=80)
        self.center_panel = CenterPanel()
        self.power_gauge = SegmentedGauge("POWER", "kW", POWER_MIN_KW, POWER_MAX_KW, segments=30, value_size=40)

        top_zone.addWidget(self.speed_gauge, 2)
        top_zone.addWidget(self.center_panel, 3)
        top_zone.addWidget(self.power_gauge, 2)

        self.bottom_bar = BottomBarStrip()
        self.bottom_bar.tech_button.clicked.connect(self.tech_requested.emit)

        root.addLayout(top_zone, 1)
        root.addWidget(self.bottom_bar)

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

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#050505"))
