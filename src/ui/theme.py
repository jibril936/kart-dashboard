from __future__ import annotations


def dark_theme_qss() -> str:
    return """
    QWidget {
        background: #0c1118;
        color: #e7edf5;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QLabel#SectionTitle {
        color: #9ab1c8;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    QFrame#Card {
        background: #151c26;
        border: 1px solid #232f3f;
        border-radius: 10px;
    }
    QLabel#KpiLabel {
        color: #8ca1b6;
        font-size: 12px;
    }
    QLabel#KpiValue {
        color: #f2f7ff;
        font-size: 23px;
        font-weight: 700;
    }
    QLabel#StatusOK { color: #53d769; font-weight: 700; }
    QLabel#StatusWARN { color: #f7b731; font-weight: 700; }
    QLabel#StatusCRIT { color: #ff5f56; font-weight: 700; }
    QFrame#AlertBanner {
        background: #1d2532;
        border: 1px solid #2d3a4e;
        border-radius: 8px;
        padding: 4px;
    }
    """
