import argparse
import signal
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt as QtCoreQt
from PyQt6.QtWidgets import QApplication

from src.core.hardware_service import DEFAULT_BMS_PORT, HardwareService
from src.core.state_store import StateStore
from src.main_window import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kart Dashboard (Raspberry Pi / PyQt6 / QtPy)"
    )
    parser.add_argument("--fs", "--fullscreen", action="store_true", help="Mode plein écran")
    parser.add_argument(
        "--port",
        type=str,
        default=DEFAULT_BMS_PORT,
        help="Port série BMS (ex: /dev/ttyUSB0)",
    )

    args = parser.parse_args()

    app = QApplication(sys.argv)

    qss_path = Path(__file__).parent / "src" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    if args.fs:
        app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    store = StateStore()
    bms_service = HardwareService(store, port=args.port)

    store.request_charge_mosfet.connect(
        bms_service.request_set_charge_mosfet,
        type=QtCoreQt.ConnectionType.QueuedConnection,
    )
    store.request_discharge_mosfet.connect(
        bms_service.request_set_discharge_mosfet,
        type=QtCoreQt.ConnectionType.QueuedConnection,
    )

    window = MainWindow(store)

    if args.fs:
        window.showFullScreen()
    else:
        window.resize(1024, 600)
        window.show()

    bms_service.start()

    def shutdown(*_sig_args):
        try:
            bms_service.stop()
        except Exception:
            pass

        app.quit()

    app.aboutToQuit.connect(shutdown)
    signal.signal(signal.SIGINT, shutdown)

    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass