import sys
from PyQt6.QtWidgets import QApplication, QLabel


def main() -> int:
    app = QApplication(sys.argv)
    w = QLabel("Kart Dashboard PyQt6 ✅")
    w.setStyleSheet("font-size: 42px; padding: 40px;")
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
