import argparse
import signal
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.core.hardware_service import DEFAULT_BMS_PORT, HardwareService
from src.core.mock_service import MockService
from src.core.state_store import StateStore
from src.main_window import MainWindow


def main() -> int:
    parser = argparse.ArgumentParser(description="Kart Dashboard (Raspberry Pi / PyQt6 / QtPy)")
    parser.add_argument("--fs", "--fullscreen", action="store_true", help="Mode plein écran")
    parser.add_argument(
        "--port",
        type=str,
        default=DEFAULT_BMS_PORT,
        help="Port série BMS (ex: /dev/ttyUSB0)",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)

    if args.fs:
        app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    store = StateStore()

    mock_service = MockService(store)
    bms_service = HardwareService(store, port=args.port)

    window = MainWindow(store)
    if args.fs:
        window.showFullScreen()
    else:
        window.resize(1024, 600)
        window.show()

    mock_service.start()
    bms_service.start()

    def shutdown(*_sig_args):
        try:
            mock_service.stop()
        except Exception:
            pass
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
