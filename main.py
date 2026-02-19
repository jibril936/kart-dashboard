import sys
import signal
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.main_window import MainWindow
from src.core.state_store import StateStore
from src.core.mock_service import MockService
from src.core.hardware_service import HardwareService

def main() -> int:
    parser = argparse.ArgumentParser(description="Kart Dashboard V3")
    parser.add_argument("--fs", "--fullscreen", action="store_true", help="Mode plein écran")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Cache le curseur si on est en plein écran
    if args.fs:
        app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    state_store = StateStore()

    simu_service = MockService(state_store)
    bms_service = HardwareService(state_store)
    window = MainWindow(state_store)
    
    if args.fs:
        window.showFullScreen()
    else:
        window.resize(1024, 600)
        window.show()

    simu_service.start()
    bms_service.start()

    def shutdown(*_args):
        simu_service.stop()
        bms_service.stop()
        app.quit()

    app.aboutToQuit.connect(shutdown)
    signal.signal(signal.SIGINT, shutdown)

    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass