from qtpy.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from qtpy.QtCore import Qt

from src.ui.screens.cluster_page import ClusterPage
from src.ui.screens.expert_page import ExpertPage
from src.ui.components.nav_bar import NavBar

try:
    from src.ui.screens.stats_page import StatsPage
except Exception:
    StatsPage = None


class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store

        self.setWindowTitle("Kart Dashboard Pro")
        self.setFixedSize(800, 480)
        self.setStyleSheet("background-color: black;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stack = QStackedWidget()

        self.page_cluster = ClusterPage(self.store)
        self.page_expert = ExpertPage(self.store)

        self.stack.addWidget(self.page_cluster)  # Index 0
        self.stack.addWidget(self.page_expert)   # Index 1

        self.page_stats = None
        if StatsPage is not None:
            try:
                self.page_stats = StatsPage(self.store)
                self.stack.addWidget(self.page_stats)  # Index 2
            except Exception as exc:
                print(f"[UI] StatsPage désactivée: {exc}")
                self.page_stats = None

        self.main_layout.addWidget(self.stack)

        self.nav_bar = NavBar()
        self.main_layout.addWidget(self.nav_bar)

        self.nav_bar.page_selected.connect(self.stack.setCurrentIndex)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_1:
            self._update_navigation(0)
        elif event.key() == Qt.Key.Key_2:
            self._update_navigation(1)
        elif event.key() == Qt.Key.Key_3 and self.stack.count() > 2:
            self._update_navigation(2)
        elif event.key() == Qt.Key.Key_F:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def _update_navigation(self, index):
        if index < self.stack.count():
            self.stack.setCurrentIndex(index)
            if hasattr(self.nav_bar, "set_active_button"):
                self.nav_bar.set_active_button(index)

    def closeEvent(self, event):
        super().closeEvent(event)