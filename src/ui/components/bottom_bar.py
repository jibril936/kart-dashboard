from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.ui.components.status_widgets import BatteryStatusWidget, TemperatureStatusWidget, ValueStatusWidget
from src.ui.visibility import set_visible_if, value_is_present


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None, *, show_charge_station: bool = True) -> None:
        super().__init__(parent)
        self.setMinimumHeight(88)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        self.battery_widget = BatteryStatusWidget()
        self.charge_station_widget = ValueStatusWidget("CHARGE STATION", "A") if show_charge_station else None
        self.steering_widget = ValueStatusWidget("STEERING", "deg")
        self.temperature_widget = TemperatureStatusWidget()
        self.brake_widget = ValueStatusWidget("BRAKE", "%")

        layout.addWidget(self.battery_widget, 2)
        if self.charge_station_widget is not None:
            layout.addWidget(self.charge_station_widget, 2)
        layout.addWidget(self.steering_widget, 2)
        layout.addWidget(self.temperature_widget, 2)
        layout.addWidget(self.brake_widget, 2)

    def set_values(
        self,
        battery_voltage: float | None,
        battery_percent: float | None,
        charging_state: bool | None,
        station_current_a: float | None,
        steering_angle_deg: float | None,
        motor_temp_c: float | None,
        brake_percent: float | None,
        temperature_label: str = "MOTOR",
    ) -> None:
        has_battery = value_is_present(battery_voltage) and value_is_present(battery_percent)
        if set_visible_if(self.battery_widget, has_battery):
            self.battery_widget.setValue(float(battery_percent), float(battery_voltage))

        has_charge_station = bool(charging_state) and value_is_present(station_current_a)
        if self.charge_station_widget is not None and set_visible_if(self.charge_station_widget, has_charge_station):
            self.charge_station_widget.setValue(float(station_current_a))

        if set_visible_if(self.steering_widget, value_is_present(steering_angle_deg)):
            self.steering_widget.setValue(float(steering_angle_deg))

        if set_visible_if(self.temperature_widget, value_is_present(motor_temp_c)):
            self.temperature_widget.setTemperature(float(motor_temp_c), temperature_label)

        if set_visible_if(self.brake_widget, value_is_present(brake_percent)):
            self.brake_widget.setValue(float(brake_percent))
