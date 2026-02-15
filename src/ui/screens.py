from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from src.core.model import KartDataModel
from src.ui.components.kart_visual_widget import KartVisualWidget
from src.ui.components.speed_gauge_oem import SpeedGaugeOEM


class WarningStrip(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ClusterWarningStrip")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(8)

        for icon in ("●", "◉", "⬢", "▲", "◆"):
            dot = QLabel(icon)
            dot.setStyleSheet("color: #8cbad7; font-size: 13px; font-weight: 700;")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(dot)

        self.message = QLabel("All systems nominal")
        self.message.setStyleSheet("color: #d8e9f6; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.message, 1)

        self.setStyleSheet(
            """
            QFrame#ClusterWarningStrip {
                background-color: #101821;
                border: 1px solid #203646;
                border-radius: 10px;
            }
            """
        )


class CurrentWidget(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._max_abs_current = 200.0
        self._current = 0.0
        self.setMinimumWidth(170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("CURRENT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #9fb7ca; font-size: 13px; font-weight: 700;")

        self.value_label = QLabel("+0 A")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: #dff8ff; font-size: 28px; font-weight: 800;")

        self.bar = QProgressBar()
        self.bar.setOrientation(Qt.Orientation.Vertical)
        self.bar.setRange(0, int(self._max_abs_current))
        self.bar.setTextVisible(False)
        self.bar.setMinimumHeight(180)

        layout.addWidget(title)
        layout.addWidget(self.value_label)
        layout.addWidget(self.bar, 1, Qt.AlignmentFlag.AlignHCenter)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #0d141d;
                border: 1px solid #1f3344;
                border-radius: 12px;
            }
            QProgressBar {
                border: 1px solid #2d465c;
                border-radius: 6px;
                background-color: #071018;
                width: 34px;
            }
            QProgressBar::chunk {
                background-color: #4bbef9;
                border-radius: 5px;
            }
            """
        )

    def set_current(self, current: float) -> None:
        self._current = float(current)
        self.value_label.setText(f"{self._current:+.0f} A")
        self.bar.setValue(min(int(self._max_abs_current), int(abs(self._current))))


class TemperatureBar(QFrame):
    def __init__(self, title: str, unit: str, minimum: float, maximum: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._min = minimum
        self._max = maximum

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self.name = QLabel(title)
        self.name.setStyleSheet("color: #a7bed0; font-size: 12px; font-weight: 700;")

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setMinimumHeight(14)

        self.value = QLabel(f"--{unit}")
        self.value.setStyleSheet("color: #dff8ff; font-size: 15px; font-weight: 700;")

        layout.addWidget(self.name)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.value)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #0f1720;
                border: 1px solid #203646;
                border-radius: 10px;
            }
            QProgressBar {
                border: 1px solid #2a4153;
                border-radius: 6px;
                background-color: #08121a;
            }
            QProgressBar::chunk {
                background-color: #5bb8ed;
                border-radius: 5px;
            }
            """
        )
        self._unit = unit

    def set_value(self, temp: float) -> None:
        clamped = min(self._max, max(self._min, float(temp)))
        ratio = (clamped - self._min) / max(1e-6, self._max - self._min)
        self.bar.setValue(int(ratio * 100))
        self.value.setText(f"{clamped:.0f}{self._unit}")


class BatteryCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        title = QLabel("BATTERY")
        title.setStyleSheet("color: #9ab3c5; font-size: 12px; font-weight: 700;")
        self.percent = QLabel("--%")
        self.percent.setStyleSheet("color: #dff8ff; font-size: 26px; font-weight: 800;")
        self.voltage = QLabel("--.- V")
        self.voltage.setStyleSheet("color: #9ed1ef; font-size: 15px; font-weight: 700;")

        layout.addWidget(title)
        layout.addWidget(self.percent)
        layout.addWidget(self.voltage)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #0f1720;
                border: 1px solid #203646;
                border-radius: 10px;
            }
            """
        )

    def set_values(self, voltage: float) -> None:
        v = float(voltage)
        soc = int(max(0.0, min(100.0, (v - 44.0) / (54.0 - 44.0) * 100.0)))
        self.percent.setText(f"{soc}%")
        self.voltage.setText(f"{v:.1f} V")


class DrivingScreen(QWidget):
    def __init__(self, model: KartDataModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = model
        self.setStyleSheet("background-color: #04070A;")

        layout = QGridLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)

        self.warning_strip = WarningStrip(self)
        self.current_widget = CurrentWidget(self)
        self.kart_visual = KartVisualWidget(self)
        self.battery_card = BatteryCard(self)
        self.motor_temp_bar = TemperatureBar("MOTOR TEMP", "°C", 0.0, 120.0, self)
        self.battery_temp_bar = TemperatureBar("BATT TEMP", "°C", 0.0, 80.0, self)

        self.speed_gauge = SpeedGaugeOEM(
            title="SPEED",
            unit="km/h",
            min_value=0,
            max_value=60,
            major_tick_step=10,
            minor_ticks_per_major=1,
        )

        left_column = QWidget(self)
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left_layout.addWidget(self.speed_gauge, 1)
        left_layout.addWidget(self.battery_card)

        temp_row = QWidget(self)
        temp_layout = QHBoxLayout(temp_row)
        temp_layout.setContentsMargins(0, 0, 0, 0)
        temp_layout.setSpacing(10)
        temp_layout.addWidget(self.motor_temp_bar, 1)
        temp_layout.addWidget(self.battery_temp_bar, 1)

        layout.addWidget(self.warning_strip, 0, 0, 1, 3)
        layout.addWidget(left_column, 1, 0)
        layout.addWidget(self.kart_visual, 1, 1)
        layout.addWidget(self.current_widget, 1, 2)
        layout.addWidget(temp_row, 2, 0, 1, 3)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)

        self._voltage = self.model.battery_pack_voltage
        self._current = self.model.battery_pack_current
        self._motor_temp = self.model.motor_temperature
        self._battery_temp = self.model.battery_temperature

        speed_signal = getattr(self.model, "speedChanged", None)
        if speed_signal is None:
            speed_signal = self.model.speed_changed
        speed_signal.connect(self.update_gauge)

        self.model.battery_pack_voltage_changed.connect(self._on_voltage_changed)
        self.model.battery_pack_current_changed.connect(self._on_current_changed)
        self.model.motor_temperature_changed.connect(self._on_motor_temp_changed)
        self.model.battery_temperature_changed.connect(self._on_battery_temp_changed)
        self.model.steering_angle_changed.connect(self.kart_visual.set_steering_angle)
        self.model.warnings_changed.connect(self._on_warnings_changed)

        self.update_gauge(self.model.speed)
        self._refresh_energy_widgets()
        self.kart_visual.set_steering_angle(self.model.steering_angle)
        self._on_warnings_changed(self.model.warnings)

    def _refresh_energy_widgets(self) -> None:
        self.battery_card.set_values(self._voltage)
        self.current_widget.set_current(self._current)
        self.motor_temp_bar.set_value(self._motor_temp)
        self.battery_temp_bar.set_value(self._battery_temp)

    def _on_voltage_changed(self, voltage: float) -> None:
        self._voltage = float(voltage)
        self._refresh_energy_widgets()

    def _on_current_changed(self, current: float) -> None:
        self._current = float(current)
        self._refresh_energy_widgets()

    def _on_motor_temp_changed(self, value: float) -> None:
        self._motor_temp = float(value)
        self.motor_temp_bar.set_value(self._motor_temp)

    def _on_battery_temp_changed(self, value: float) -> None:
        self._battery_temp = float(value)
        self.battery_temp_bar.set_value(self._battery_temp)

    def _on_warnings_changed(self, warnings: list[str]) -> None:
        self.warning_strip.message.setText("All systems nominal" if not warnings else " | ".join(warnings).replace("_", " ").title())

    def update_gauge(self, value: float) -> None:
        self.speed_gauge.set_value(value)


class TechScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #091530;")

        layout = QGridLayout(self)
        label = QLabel("TECH")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)


class GraphsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

        layout = QGridLayout(self)
        label = QLabel("GRAPHS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)
