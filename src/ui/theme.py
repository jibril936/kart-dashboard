from __future__ import annotations


def dark_theme_qss() -> str:
    return """
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #070b12, stop:0.5 #05080f, stop:1 #020408);
        color: #e7edf5;
        font-family: 'Bahnschrift', 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px;
    }
    QStackedWidget, QListWidget, QFrame, QWidget#ClusterScreen, QWidget#TechScreen {
        background: transparent;
    }

    QPushButton#NavButton {
        color: #d7e5f3;
        background: rgba(29, 41, 63, 0.86);
        border: 1px solid #435992;
        border-radius: 16px;
        padding: 5px 16px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.7px;
    }

    QPushButton#TechButton {
        color: #c9f8ff;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(17,52,78,0.95), stop:1 rgba(4,16,28,0.95));
        border: 1px solid #5cc8e6;
        border-radius: 5px;
        padding: 6px 22px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
    }
    QPushButton#TechButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(24,76,112,0.98), stop:1 rgba(5,23,41,0.98));
        border: 1px solid #88eeff;
    }

    QFrame#BottomBarStrip {
        background: rgba(5, 10, 18, 0.85);
        border-top: 1px solid #325779;
        border-bottom: 1px solid #101d2b;
        border-left: none;
        border-right: none;
        border-radius: 0;
    }
    """
