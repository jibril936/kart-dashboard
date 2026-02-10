from __future__ import annotations

import logging
import sys
from pathlib import Path

from src.config.loader import AppConfig, load_config
from src.data.logger import TelemetryLogger
from src.data.sources import DataSource, I2CDataSource, SimulatedDataSource
from src.data.worker import DataWorker
from src.models.telemetry import Telemetry
from src.models.telemetry_model import TelemetryModel
from src.qt_compat import QApplication, QThread
from src.ui.dashboard import DashboardWindow


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_source(config: AppConfig) -> DataSource:
    if config.source == "i2c":
        i2c_source = I2CDataSource(bus=config.i2c.bus, address=config.i2c.address)
        if not i2c_source.is_available:
            logging.getLogger(__name__).warning("I2C unavailable, falling back to simulated source")
            simulated = SimulatedDataSource()
            simulated.inject_startup_alert("I2C indisponible: fallback en mode simulated")
            return simulated
        return i2c_source
    return SimulatedDataSource()


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
    worker_thread = QThread()
    worker.moveToThread(worker_thread)

    telemetry_model = TelemetryModel(config.alerts)

    logger = TelemetryLogger(Path(config.logging.path)) if config.logging.enabled else None

    def on_telemetry(telemetry: Telemetry) -> None:
        window.update_telemetry(telemetry)
        if logger:
            logger.log(telemetry)

    worker.telemetry_received.connect(telemetry_model.process)
    telemetry_model.telemetry_updated.connect(on_telemetry)

    worker_thread.started.connect(worker.start)
    worker_thread.start()

    exit_code = app.exec()

    worker.stop()
    worker_thread.quit()
    worker_thread.wait()
    if logger:
        logger.close()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
