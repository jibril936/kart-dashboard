from __future__ import annotations

import argparse
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.config.settings import load_settings
from src.core.state import default_state
from src.core.store import StateStore
from src.services.fake_data_service import FakeDataService
from src.ui.main_window import DashboardMainWindow
from src.ui.theme import dark_theme_qss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kart dashboard — Cluster + Tech")
    parser.add_argument("--demo", action="store_true", help="Use fake data service")
    parser.add_argument("--scenario", default="normal", choices=["normal", "acceleration", "battery_drop", "overheat", "sensor_ko"])
    parser.add_argument("--ui-scale", type=float, default=1.0, help="UI scaling factor for compact displays")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()

    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme_qss())

    window = DashboardMainWindow(ui_scale=max(0.6, min(2.0, args.ui_scale)))
    window.resize(1440, 900)

    store = StateStore(default_state())
    service = FakeDataService(scenario=args.scenario)

    store.state_changed.connect(window.render)

    ui_hz = max(20, min(30, settings.ui_hz))
    timer = QTimer()
    timer.setInterval(int(1000 / ui_hz))
    timer.timeout.connect(lambda: store.update(service.sample()))
    timer.start()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
