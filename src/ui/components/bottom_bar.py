from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.ui.components.status_widgets import BatteryStatusWidget, MeterBarWidget, TemperatureStatusWidget
from src.ui.visibility import set_visible_if, value_is_present


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(88)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        self.battery_widget = BatteryStatusWidget()
        self.power_widget = MeterBarWidget("POWER", "#6a89ff")
        self.temp_bar_widget = MeterBarWidget("TEMP", "#ff8b5a")
        self.regen_widget = MeterBarWidget("REGEN", "#5dbba9")
        self.temperature_widget = TemperatureStatusWidget()

        layout.addWidget(self.battery_widget, 2)
        layout.addWidget(self.power_widget, 2)
        layout.addWidget(self.temp_bar_widget, 2)
        layout.addWidget(self.regen_widget, 2)
        layout.addWidget(self.temperature_widget, 2)

    def set_values(
        self,
        battery_voltage: float | None,
        battery_percent: float | None,
        power_ratio: float | None,
        regen_ratio: float | None,
        motor_temp_c: float | None,
        temperature_label: str = "MOTOR",
    ) -> None:
        has_battery = value_is_present(battery_voltage) and value_is_present(battery_percent)
        if set_visible_if(self.battery_widget, has_battery):
            self.battery_widget.setValue(float(battery_percent), float(battery_voltage))

        if set_visible_if(self.power_widget, value_is_present(power_ratio)):
            self.power_widget.setRatio(float(power_ratio))

        temp_bar_ratio = None if motor_temp_c is None else max(0.0, min(1.0, motor_temp_c / 120.0))
        if set_visible_if(self.temp_bar_widget, value_is_present(temp_bar_ratio)):
            self.temp_bar_widget.setRatio(float(temp_bar_ratio))

        if set_visible_if(self.regen_widget, value_is_present(regen_ratio)):
            self.regen_widget.setRatio(float(regen_ratio))

        if set_visible_if(self.temperature_widget, value_is_present(motor_temp_c)):
            self.temperature_widget.setTemperature(float(motor_temp_c), temperature_label)
