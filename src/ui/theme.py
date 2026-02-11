from __future__ import annotations


def build_stylesheet() -> str:
    return """
    QWidget {
        background: qradialgradient(cx:0.5, cy:0.46, radius:0.95,
                                    fx:0.5, fy:0.38,
                                    stop:0 #101A2A,
                                    stop:0.45 #0C1423,
                                    stop:1 #05090F);
        color: #F4F8FF;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QPushButton {
        background: rgba(29, 38, 60, 0.86);
        border: 1px solid rgba(103, 122, 161, 0.35);
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 14px;
        font-weight: 600;
    }
    QPushButton:hover { background: rgba(36, 47, 73, 0.92); }
    QPushButton[secondary="true"] {
        border-radius: 10px;
        font-size: 13px;
        padding: 7px 12px;
    }
    QFrame[card="true"] {
        background: rgba(16, 23, 40, 0.95);
        border: 1px solid rgba(69, 88, 126, 0.45);
        border-radius: 16px;
    }
    QFrame[topBar="true"] {
        background: rgba(12, 20, 34, 0.78);
        border: 1px solid rgba(80, 98, 131, 0.24);
        border-radius: 14px;
    }
    QFrame[dial="true"] {
        background: qradialgradient(cx:0.5, cy:0.4, radius:0.9,
                                    stop:0 rgba(33, 47, 76, 0.84),
                                    stop:1 rgba(12, 17, 29, 0.82));
        border: 1px solid rgba(118, 137, 170, 0.28);
        border-radius: 180px;
    }
    QFrame[centerPanel="true"] {
        background: rgba(11, 17, 29, 0.88);
        border: 1px solid rgba(113, 131, 161, 0.3);
        border-radius: 18px;
    }
    QFrame[clusterTile="true"] {
        background: rgba(24, 33, 52, 0.52);
        border: 1px solid rgba(102, 120, 155, 0.18);
        border-radius: 13px;
    }
    QLabel[kpi="true"] {
        color: #97A8C5;
        font-size: 12px;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    }
    QLabel[value="true"] {
        color: #F8FBFF;
        font-size: 30px;
        font-weight: 700;
    }
    QLabel[clusterTitle="true"] {
        color: #DDE8FA;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.2px;
    }
    QLabel[clock="true"] {
        color: #DCE8FF;
        font-size: 18px;
        font-weight: 600;
    }
    QLabel[dialValue="true"] {
        color: #F6FBFF;
    }
    QLabel[statusRow="true"] {
        color: #BCCCE8;
        font-size: 14px;
    }
    QLabel[tileValue="true"] {
        color: #F2F8FF;
        font-size: 28px;
        font-weight: 700;
    }
    QLabel[tileUnit="true"] {
        color: #8EA0C3;
        font-size: 12px;
    }
    QLabel[alertLine="info"] {
        color: #96B5E9;
        font-size: 13px;
        font-weight: 600;
    }
    QLabel[alertLine="warning"] {
        color: #FFC468;
        font-size: 13px;
        font-weight: 700;
    }
    QLabel[alertLine="critical"] {
        color: #FF7E8C;
        font-size: 13px;
        font-weight: 700;
    }
    QLabel[warningIcon="true"] {
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
        border-radius: 12px;
        border: 1px solid rgba(124, 140, 169, 0.35);
        background: rgba(96, 110, 136, 0.15);
        color: rgba(173, 188, 216, 0.75);
        font-size: 12px;
        font-weight: 700;
    }
    QLabel[warningIcon="true"][warningActive="true"] {
        border: 1px solid rgba(255, 130, 118, 0.8);
        background: rgba(255, 106, 88, 0.2);
        color: #FFD4CE;
    }
    """
