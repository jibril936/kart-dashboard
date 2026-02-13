from __future__ import annotations

import argparse
import os
import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication

from src.config.settings import load_settings
from src.core.state import default_state
from src.core.store import StateStore
from src.services.fake_data_service import FakeDataService
from src.ui.main_window import DashboardMainWindow
from src.ui.theme import dark_theme_qss


def _apply_window_mode(window: DashboardMainWindow, fullscreen_enabled: bool, maximized_enabled: bool) -> None:
    if fullscreen_enabled:
        window.show()

        def _apply_fullscreen() -> None:
            screen = window.screen()
            if screen is not None:
                window.setGeometry(screen.geometry())
            window.showFullScreen()

        QTimer.singleShot(0, _apply_fullscreen)

        def _verify_fullscreen() -> None:
            if not window.isFullScreen():
                _apply_fullscreen()
            window.apply_fullscreen_cursor()

        QTimer.singleShot(200, _verify_fullscreen)
        return

    if maximized_enabled:
        window.showMaximized()
        return

    window.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kart dashboard — Cluster + Tech")
    parser.add_argument("--demo", action="store_true", help="Use fake data service")
    parser.add_argument("--scenario", default="normal", choices=["normal", "acceleration", "battery_drop", "overheat", "sensor_ko"])
    parser.add_argument("--ui-scale", type=float, default=1.0, help="UI scaling factor for compact displays")
    parser.add_argument("--fullscreen", action="store_true", help="Force fullscreen mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()

    app = QApplication(sys.argv)
    app.setStyleSheet(dark_theme_qss())

    window = DashboardMainWindow(ui_scale=max(0.6, min(2.0, args.ui_scale)))

    fullscreen_enabled = args.fullscreen or os.getenv("KART_FULLSCREEN") == "1"
    maximized_enabled = os.getenv("KART_MAXIMIZED") == "1"
    hide_cursor_enabled = os.getenv("KART_HIDE_CURSOR") == "1"
    kiosk_enabled = os.getenv("KART_KIOSK") == "1"

    if kiosk_enabled and fullscreen_enabled:
        window.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

    if not fullscreen_enabled and not maximized_enabled:
        window.resize(1440, 900)

    store = StateStore(default_state())
    service = FakeDataService(scenario=args.scenario)

    store.state_changed.connect(window.render)

    ui_hz = max(20, min(30, settings.ui_hz))
    timer = QTimer()
    timer.setInterval(int(1000 / ui_hz))
    timer.timeout.connect(lambda: store.update(service.sample()))
    timer.start()

    if fullscreen_enabled:
        window.enable_escape_fullscreen()
    window.set_hide_cursor_in_fullscreen(hide_cursor_enabled)

    QTimer.singleShot(0, lambda: _apply_window_mode(window, fullscreen_enabled, maximized_enabled))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
