from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from src.ui.screens.cluster_page import ClusterPage


class MainWindow(QMainWindow):
    """Main OLED-like dashboard shell using stacked pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard")
        self.resize(1024, 600)

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self._create_pages()
        self._apply_default_theme()
        self._load_stylesheet()

    def _create_pages(self) -> None:
        cluster_page = ClusterPage(self)
        self.stack.addWidget(cluster_page)
        self.stack.setCurrentWidget(cluster_page)

    def _apply_default_theme(self) -> None:
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).resolve().parent / "styles.qss"
        if not qss_path.exists():
            return

        stylesheet = qss_path.read_text(encoding="utf-8").strip()
        if stylesheet:
            self.setStyleSheet(f"{self.styleSheet()}\n{stylesheet}")
