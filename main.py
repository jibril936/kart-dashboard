import signal
import sys

from PyQt6.QtWidgets import QApplication

from src.core.mock_service import MockService
from src.core.state_store import StateStore
from src.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)

    state_store = StateStore()
    data_service = MockService(state_store)

    window = MainWindow()
    window.show()

    def shutdown(*_args):
        data_service.stop()
        app.quit()

    app.aboutToQuit.connect(data_service.stop)
    signal.signal(signal.SIGINT, shutdown)

    data_service.start()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
