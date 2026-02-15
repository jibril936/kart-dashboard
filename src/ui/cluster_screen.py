from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient
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
        segments: int = 40,
        value_font_size: int = 66,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = float(minimum)
        self._max = float(maximum)
        self._segments = 42 if int(segments) != 42 else int(segments)
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
        self.unit_label.setFont(QFont("Roboto Mono", 12, QFont.Weight.Medium))
        self.unit_label.setStyleSheet("color: #888888; background: transparent; border: none;")

        root.addWidget(self.title_label)
        root.addStretch(1)
        root.addWidget(self.unit_label)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(26)
        glow.setOffset(0, 0)
        glow.setColor(QColor("#00FFFF"))
        self.setGraphicsEffect(glow)

        self._anim = QPropertyAnimation(self, b"displayValue", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

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
        center_y = h / 2 + 8

        arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        base_glow = QRadialGradient(center_x, center_y, radius * 1.22)
        base_glow.setColorAt(0.0, QColor(10, 24, 36, 8))
        base_glow.setColorAt(0.55, QColor(11, 34, 48, 30))
        base_glow.setColorAt(1.0, QColor(8, 14, 18, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base_glow)
        painter.drawEllipse(arc_rect.adjusted(-32, -32, 32, 32))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#18232D"), 26, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(arc_rect, int(-220 * 16), int(260 * 16))

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
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(-5, -18, 10, 30)
                painter.setBrush(QColor(163, 249, 255, 110))
                painter.drawRect(-2, -16, 4, 26)
            else:
                painter.setBrush(QColor("#242F39"))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(-2, -14, 4, 24)
            painter.restore()

        ratio_angle = start_angle + (max(0.0, min(1.0, ratio)) * sweep)
        pointer_rad = math.radians(ratio_angle)
        tail = radius * 0.10
        tip = radius * 0.78
        tip_x = center_x + math.cos(pointer_rad) * tip
        tip_y = center_y + math.sin(pointer_rad) * tip
        tail_x = center_x - math.cos(pointer_rad) * tail
        tail_y = center_y - math.sin(pointer_rad) * tail

        painter.setPen(QPen(QColor(91, 236, 255, 100), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(tail_x), int(tail_y), int(tip_x), int(tip_y))
        painter.setPen(QPen(QColor("#F2FCFF"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(tail_x), int(tail_y), int(tip_x), int(tip_y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#9FE9FF"))
        painter.drawEllipse(int(center_x - 7), int(center_y - 7), 14, 14)
        painter.setBrush(QColor("#121C24"))
        painter.drawEllipse(int(center_x - 3), int(center_y - 3), 6, 6)

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Roboto Mono", self._value_font_size, QFont.Weight.Bold))
        painter.drawText(self.rect().adjusted(0, -18, 0, 0), Qt.AlignmentFlag.AlignCenter, self._formatted_value())


class CockpitPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #151515;
                border: 1px solid #222222;
                border-radius: 25px;
                background: qlineargradient(
                    x1: 0,
                    y1: 0,
                    x2: 0,
                    y2: 1,
                    stop: 0 #1A1A1A,
                    stop: 1 #121212
                );
            }
            """
        )


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

        self.speed_gauge = SegmentedGauge("SPEED", "km/h", SPEED_MIN_KMH, SPEED_MAX_KMH, segments=40, value_font_size=72)
        self.center_panel = CenterPanel()
        self.power_gauge = SegmentedGauge("POWER", "kW", POWER_MIN_KW, POWER_MAX_KW, segments=40, value_font_size=64)

        left_panel = CockpitPanel()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.addWidget(self.speed_gauge)

        center_panel = CockpitPanel()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(14, 14, 14, 14)
        center_layout.addWidget(self.center_panel)

        right_panel = CockpitPanel()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.addWidget(self.power_gauge)

        self.bottom_bar = BottomBarStrip()
        self.bottom_bar.tech_button.clicked.connect(self.tech_requested.emit)

        grid.addWidget(left_panel, 0, 0)
        grid.addWidget(center_panel, 0, 1)
        grid.addWidget(right_panel, 0, 2)
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
