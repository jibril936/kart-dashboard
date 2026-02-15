from PyQt6.QtWidgets import QMainWindow, QStackedWidget


class MainWindow(QMainWindow):
    """Minimal dashboard shell with an empty stacked widget."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard")
        self.resize(1024, 600)
        self.setStyleSheet("background-color: #000000;")

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
