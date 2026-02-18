import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import de la structure
from src.main_window import MainWindow
from src.core.state_store import StateStore
from src.core.mock_service import MockService
from src.core.hardware_service import HardwareService

def main() -> int:
    app = QApplication(sys.argv)
    
    # Cache le curseur de la souris (Look pro sur la Pi)
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)

    state_store = StateStore()

    # Services
    simu_service = MockService(state_store)
    bms_service = HardwareService(state_store)

    window = MainWindow(state_store)
    
    # --- PASSAGE EN PLEIN ÉCRAN ---
    window.showFullScreen() 

    print("--- Démarrage des services ---")
    simu_service.start()
    bms_service.start()

    def shutdown(*_args):
        print("\nArrêt en cours...")
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