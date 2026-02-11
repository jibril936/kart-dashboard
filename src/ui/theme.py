from __future__ import annotations


def dark_theme_qss() -> str:
    return """
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1119, stop:1 #0a0f15);
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
    QLabel#StatusOK { color: #53d769; font-weight: 700; }
    QLabel#StatusWARN { color: #f7b731; font-weight: 700; }
    QLabel#StatusCRIT { color: #ff5f56; font-weight: 700; }

    QFrame#SectionPanel {
        background: rgba(18, 27, 39, 0.78);
        border: 1px solid #223042;
        border-radius: 10px;
    }
    QFrame#KpiLine {
        background: rgba(14, 21, 31, 0.9);
        border: 1px solid #223447;
        border-radius: 8px;
    }
    QListWidget#AlertList {
        background: rgba(14, 21, 31, 0.7);
        border: 1px solid #223447;
        border-radius: 8px;
        outline: none;
    }

    QLabel#IndicatorIdle {
        color: #6f8299;
        background: rgba(16, 26, 39, 0.6);
        border: 1px solid #26384a;
        border-radius: 14px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 600;
    }
    QLabel#IndicatorActive {
        color: #f2f7ff;
        background: rgba(38, 74, 109, 0.8);
        border: 1px solid #5f89b3;
        border-radius: 14px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
    }
    QFrame#MiniGauge {
        background: rgba(18, 27, 39, 0.78);
        border: 1px solid #223042;
        border-radius: 10px;
        min-width: 280px;
    }
    QLabel#MiniGaugeTitle {
        color: #8ca1b6;
        font-size: 12px;
    }
    QLabel#MiniGaugeValue {
        color: #f2f7ff;
        font-size: 14px;
        font-weight: 700;
    }
    QProgressBar {
        border: 1px solid #28394c;
        border-radius: 5px;
        background: #131b24;
    }
    QProgressBar::chunk { border-radius: 4px; background: #53d769; }
    QProgressBar[status="WARN"]::chunk { background: #f7b731; }
    QProgressBar[status="CRIT"]::chunk { background: #ff5f56; }

    QPushButton#NavButton {
        color: #d7e5f3;
        background: rgba(34, 52, 72, 0.85);
        border: 1px solid #3c5977;
        border-radius: 16px;
        padding: 6px 16px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.6px;
    }
    QPushButton#NavButton:hover {
        background: rgba(48, 75, 103, 0.95);
    }
    """
