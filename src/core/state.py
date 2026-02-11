from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class VehicleTechState:
    """Single MVP state model for technical vehicle telemetry."""

    # 1) Battery / Charge
    battery_voltage_V: float = 52.0
    battery_charge_current_A: float = 8.0
    charging_state: bool = True

    # 2) Charging station
    station_frequency_Hz: float = 50.0
    station_current_A: float = 16.0

    # 3) Steering
    steering_pot_voltage_V: float = 2.5
    steering_angle_deg: float = 0.0
    steering_current_A: float = 1.0

    # 4) Traction / Brake
    speed_kmh: float = 0.0
    rpm: int = 0
    brake_state: float = 0.0

    # 5) Temperature
    motor_temp_C: float = 38.0

    # timestamps
    sample_timestamp_ms: int = 0
    field_timestamps_ms: dict[str, int] = field(default_factory=dict)


def utc_now_ms() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)


def default_state() -> VehicleTechState:
    now = utc_now_ms()
    state = VehicleTechState(sample_timestamp_ms=now)
    state.field_timestamps_ms = {
        "battery_voltage_V": now,
        "battery_charge_current_A": now,
        "charging_state": now,
        "station_frequency_Hz": now,
        "station_current_A": now,
        "steering_pot_voltage_V": now,
        "steering_angle_deg": now,
        "steering_current_A": now,
        "speed_kmh": now,
        "rpm": now,
        "brake_state": now,
        "motor_temp_C": now,
    }
    return state
