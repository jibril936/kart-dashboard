from __future__ import annotations


def dark_theme_qss() -> str:
    return """
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #090f18, stop:0.55 #080d16, stop:1 #05080e);
        color: #e7edf5;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px;
    }
    QStackedWidget, QListWidget, QFrame, QWidget#ClusterScreen, QWidget#TechScreen {
        background: transparent;
    }
    QLabel#SectionTitle {
        color: #9ab1c8;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }
    QLabel#KpiValue {
        color: #f2f7ff;
        font-size: 16px;
        font-weight: 700;
        min-width: 56px;
    }
    QLabel#StatusOK { color: #53d7be; font-weight: 700; }
    QLabel#StatusWARN { color: #ffbf58; font-weight: 700; }
    QLabel#StatusCRIT { color: #ff6d64; font-weight: 700; }

    QFrame#SectionPanel {
        background: rgba(12, 19, 30, 0.78);
        border: 1px solid #223042;
        border-radius: 10px;
    }
    QFrame#KpiLine {
        background: rgba(10, 16, 26, 0.9);
        border: 1px solid #223447;
        border-radius: 8px;
    }
    QListWidget#AlertList {
        background: rgba(12, 18, 30, 0.7);
        border: 1px solid #223447;
        border-radius: 8px;
        outline: none;
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
    QPushButton#NavButton:hover {
        background: rgba(43, 62, 95, 0.96);
        border: 1px solid #6982ca;
    }

    QFrame#BottomBarStrip {
        background: rgba(7, 14, 26, 0.95);
        border-top: 1px solid #2a4365;
        border-bottom: 1px solid #13253e;
        border-left: none;
        border-right: none;
        border-radius: 0;
    }
    """
