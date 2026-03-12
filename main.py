import argparse
import signal
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt as QtCoreQt
from PyQt6.QtWidgets import QApplication

from src.core.borne_i2c_service import BorneI2CService
from src.core.charger_i2c_service import ChargerI2CService
from src.core.hardware_service import DEFAULT_BMS_PORT, HardwareService
from src.core.state_store import StateStore
from src.core.variator_i2c_service import VariatorI2CService
from src.main_window import MainWindow
from src.core.charger_i2c_service import ChargerI2CService

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
    parser.add_argument("--i2c-bus", type=int, default=1, help="Bus I2C")
    parser.add_argument(
        "--variator-addr",
        type=lambda x: int(x, 0),
        default=0x22,
        help="Adresse I2C variateur",
    )
    parser.add_argument(
        "--charger-addr",
        type=lambda x: int(x, 0),
        default=0x24,
        help="Adresse I2C chargeur",
    )
    parser.add_argument(
        "--borne-addr",
        type=lambda x: int(x, 0),
        default=0x56,
        help="Adresse I2C borne",
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

    variator_service = VariatorI2CService(
        bus_id=args.i2c_bus,
        address=args.variator_addr,
        parent=app,
    )
    charger_service = ChargerI2CService(
        bus_id=args.i2c_bus,
        address=args.charger_addr,
        parent=app,
    )
    borne_service = BorneI2CService(
        bus_id=args.i2c_bus,
        address=args.borne_addr,
        parent=app,
    )

    store.variator_service = variator_service
    store.charger_service = charger_service
    store.borne_service = borne_service

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
    variator_service.start()
    charger_service.start()
    borne_service.start()

    def shutdown(*_sig_args):
        for svc in (borne_service, charger_service, variator_service):
            try:
                svc.stop()
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