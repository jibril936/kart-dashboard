from __future__ import annotations

import argparse
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.config.settings import load_settings
from src.core.store import StateStore
from src.core.state import default_state
from src.services.fake_data_service import FakeDataService
from src.ui.main_window import TechMainWindow
from src.ui.theme import dark_theme_qss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TECH app — Informations techniques véhicule")
    parser.add_argument("--demo", action="store_true", help="Use fake data service")
    parser.add_argument("--scenario", default="normal", choices=["normal", "battery_drop", "overheat", "sensor_ko"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()

    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme_qss())

    window = TechMainWindow()
    window.resize(1360, 860)

    store = StateStore(default_state())
    service = FakeDataService(scenario=args.scenario)

    store.state_changed.connect(window.render)

    timer = QTimer()
    timer.setInterval(int(1000 / max(1, settings.ui_hz)))
    timer.timeout.connect(lambda: store.update(service.sample()))
    timer.start()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
