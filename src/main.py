from __future__ import annotations

import argparse
import logging
import os
import sys

from src.config.loader import load_config
from src.core.alerts import AlertEngine
from src.core.store import StateStore, default_state
from src.qt_compat import QApplication, QThread
from src.services.fake import FakeDataService
from src.services.poller import DataPoller
from src.ui.details_screen import DetailsScreen
from src.ui.main_window import MainWindow
from src.ui.theme import build_stylesheet


def setup_logging() -> None:
    level = os.environ.get("KART_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kart dashboard")
    parser.add_argument("--demo", action="store_true", help="Force fake demo data")
    parser.add_argument(
        "--scenario",
        choices=["normal", "acceleration", "battery_drop", "overheat", "sensor_ko"],
        help="Demo scenario",
    )
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()
    config = load_config()

    if args.demo:
        config.source = "demo"
    if args.scenario:
        config.demo_scenario = args.scenario

    app = QApplication(sys.argv)
    app.setStyleSheet(build_stylesheet())

    store = StateStore(default_state())
    alerts = AlertEngine(config)
    details = DetailsScreen(store)
    window = MainWindow(config, details)

    if config.fullscreen and not config.debug:
        window.showFullScreen()
    else:
        window.resize(1440, 860)
        window.show()

    service = FakeDataService(scenario=config.demo_scenario)

    poller = DataPoller(service, data_hz=config.data_hz)
    thread = QThread()
    poller.moveToThread(thread)

    def on_sample(sample: object, stale_ms: int) -> None:
        state = alerts.evaluate(sample, stale_ms, store.state.alert_history)
        store.update(state)

    poller.sample_ready.connect(on_sample)
    store.state_changed.connect(window.render)

    thread.started.connect(poller.start)
    thread.start()

    exit_code = app.exec()
    poller.stop()
    thread.quit()
    thread.wait()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
