from __future__ import annotations


def build_stylesheet() -> str:
    return """
    QWidget {
        background: #070B14;
        color: #F4F8FF;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QPushButton {
        background: #151C2F;
        border: 1px solid #24304F;
        border-radius: 12px;
        padding: 12px 20px;
        font-size: 17px;
        font-weight: 600;
    }
    QPushButton:hover { background: #1B2540; }
    QFrame[card="true"] {
        background: #101728;
        border: 1px solid #202B45;
        border-radius: 16px;
    }
    QLabel[kpi="true"] {
        color: #9BA9C2;
        font-size: 14px;
        text-transform: uppercase;
    }
    QLabel[value="true"] {
        color: #F8FBFF;
        font-size: 30px;
        font-weight: 700;
    }
    """
