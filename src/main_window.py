from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QVBoxLayout, QWidget


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
        pages = [
            self._build_page("Page 1 - Driving"),
            self._build_page("Page 2 - BMS"),
            self._build_page("Page 3 - Safety"),
        ]
        for page in pages:
            self.stack.addWidget(page)

    def _build_page(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        return page

    def _apply_default_theme(self) -> None:
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).resolve().parent / "styles.qss"
        if not qss_path.exists():
            return

        stylesheet = qss_path.read_text(encoding="utf-8").strip()
        if stylesheet:
            self.setStyleSheet(f"{self.styleSheet()}\n{stylesheet}")
