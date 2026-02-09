import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from src.config.loader import AppConfig, load_config
from src.data.logger import TelemetryLogger
from src.data.sources.i2c import I2CSource
from src.data.sources.simulated import SimulatedSource
from src.data.worker import DataWorker
from src.ui.dashboard import DashboardWindow


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_source(config: AppConfig):
    if config.source == "i2c":
        return I2CSource(bus=config.i2c.bus, address=config.i2c.address)
    return SimulatedSource()


def main() -> int:
    setup_logging()
    config = load_config()

    app = QApplication(sys.argv)
    window = DashboardWindow(refresh_hz=config.refresh_hz)

    if config.fullscreen and not config.debug:
        window.showFullScreen()
    else:
        window.resize(1280, 720)
        window.show()

    source = build_source(config)
    worker = DataWorker(source, refresh_hz=config.refresh_hz)
    thread = QThread()
    worker.moveToThread(thread)

    logger = None
    if config.logging.enabled:
        logger = TelemetryLogger(Path(config.logging.path))

    def handle_telemetry(telemetry):
        window.update_telemetry(telemetry)
        if logger:
            logger.log(telemetry)

    worker.telemetry_received.connect(handle_telemetry)
    thread.started.connect(worker.start)
    thread.start()

    exit_code = app.exec()

    worker.stop()
    thread.quit()
    thread.wait()
    if logger:
        logger.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
