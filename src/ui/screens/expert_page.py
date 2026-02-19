from __future__ import annotations

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.components.battery_elements import BMSSummaryCard, BatteryIcon


class Lamp(QFrame):
    """Voyant compact ON/OFF."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._on = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(50)
        self.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:14px; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.dot = QLabel("●")
        self.dot.setStyleSheet("color:#222; font-size:18px;")
        layout.addWidget(self.dot)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:11px;")
        layout.addWidget(self.lbl_title)

        layout.addStretch(1)

        self.badge = QLabel("OFF")
        self.badge.setFixedWidth(56)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet(
            "background:#111; border:1px solid #222; border-radius:10px; "
            "color:#666; font-family:Orbitron; font-weight:bold; font-size:10px;"
        )
        layout.addWidget(self.badge)

    def set_on(self, state: bool, color_on: str = "#00FFD0") -> None:
        self._on = bool(state)
        if self._on:
            self.dot.setStyleSheet(f"color:{color_on}; font-size:18px;")
            self.badge.setText("ON")
            self.badge.setStyleSheet(
                f"background:{color_on}; border:none; border-radius:10px; "
                "color:#000; font-family:Orbitron; font-weight:bold; font-size:10px;"
            )
        else:
            self.dot.setStyleSheet("color:#222; font-size:18px;")
            self.badge.setText("OFF")
            self.badge.setStyleSheet(
                "background:#111; border:1px solid #222; border-radius:10px; "
                "color:#666; font-family:Orbitron; font-weight:bold; font-size:10px;"
            )


class AlertLamp(Lamp):
    """Voyant d'alerte (OFF gris / ON rouge)."""
    def set_alert(self, state: bool) -> None:
        super().set_on(state, color_on="#FF4040")


class ExpertPage(QWidget):
    """
    Expert page:
      - Carte "BMS HEALTH" cliquable
      - Overlay plein écran "FULL BMS CONTROL" (resizeEvent)
          * Grille 4x4 BatteryIcons
          * MOSFET STATUS (Charge/Décharge)
          * BMS DIAGNOSTIC (OV/OT/SC) basé sur bitmask
    """

    # Bits diagnostics (placeholder -> ajuste si ta table JK diffère)
    BIT_OV = 0x0004
    BIT_OT = 0x0008
    BIT_SC = 0x0010

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self._vpack = 0.0
        self._vmin = 0.0
        self._vmax = 0.0
        self._delta = 0.0
        self._bitmask = 0

        self._build_main()
        self._build_overlay()
        self._connect_signals()

    # -----------------
    # Main page
    # -----------------
    def _build_main(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.card = BMSSummaryCard(self)
        self.card.clicked.connect(self.show_overlay)
        row.addWidget(self.card)

        # placeholder à droite (tu peux mettre d’autres cards)
        spacer = QFrame(self)
        spacer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        spacer.setStyleSheet("QFrame { background:#060606; border:1px dashed #222; border-radius:16px; }")
        row.addWidget(spacer, 1)

        layout.addLayout(row)
        layout.addStretch(1)

    # -----------------
    # Overlay
    # -----------------
    def _build_overlay(self) -> None:
        self.overlay = QFrame(self)
        self.overlay.hide()
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.overlay.setStyleSheet("QFrame { background-color: rgba(0, 0, 0, 250); border:none; }")

        root = QVBoxLayout(self.overlay)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(14)

        # Header (fixe)
        header = QFrame(self.overlay)
        header.setFixedHeight(58)
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:14px; }")

        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 10, 14, 10)
        hl.setSpacing(10)

        title = QLabel("FULL BMS CONTROL")
        title.setStyleSheet("color: cyan; font-family: Orbitron; font-size: 18px; font-weight: bold;")
        hl.addWidget(title)

        hl.addStretch(1)

        self.btn_close = QPushButton("CLOSE")
        self.btn_close.setFixedSize(110, 40)
        self.btn_close.setStyleSheet(
            "QPushButton { background:#111; color:#DDD; border:1px solid #222; border-radius:12px; "
            "font-family:Orbitron; font-weight:bold; }"
            "QPushButton:pressed { background:#00FFD0; color:#000; border:none; }"
        )
        self.btn_close.clicked.connect(self.overlay.hide)
        hl.addWidget(self.btn_close)

        root.addWidget(header)

        # Content row: grid left + panels right
        content = QHBoxLayout()
        content.setSpacing(16)

        # Cells grid (4x4)
        grid_wrap = QFrame(self.overlay)
        grid_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        grid_wrap.setStyleSheet("QFrame { background:#050505; border:1px solid #222; border-radius:16px; }")
        grid_layout = QVBoxLayout(grid_wrap)
        grid_layout.setContentsMargins(14, 14, 14, 14)
        grid_layout.setSpacing(10)

        lbl_cells = QLabel("CELLS (4x4)")
        lbl_cells.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:11px;")
        grid_layout.addWidget(lbl_cells)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i + 1, grid_wrap)
            self.cell_widgets.append(icon)
            grid.addWidget(icon, i // 4, i % 4, Qt.AlignmentFlag.AlignCenter)

        grid_layout.addLayout(grid, 1)
        content.addWidget(grid_wrap, 1)

        # Right panels
        right = QVBoxLayout()
        right.setSpacing(16)

        # MOSFET STATUS panel
        mos_panel = QFrame(self.overlay)
        mos_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        mos_panel.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:16px; }")
        mos_l = QVBoxLayout(mos_panel)
        mos_l.setContentsMargins(14, 14, 14, 14)
        mos_l.setSpacing(10)

        mos_title = QLabel("MOSFET STATUS")
        mos_title.setStyleSheet("color: cyan; font-family:Orbitron; font-size:11px;")
        mos_l.addWidget(mos_title)

        self.lamp_charge = Lamp("CHARGE")
        self.lamp_discharge = Lamp("DISCHARGE")
        mos_l.addWidget(self.lamp_charge)
        mos_l.addWidget(self.lamp_discharge)
        mos_l.addStretch(1)

        # BMS DIAGNOSTIC panel
        diag_panel = QFrame(self.overlay)
        diag_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        diag_panel.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:16px; }")
        diag_l = QVBoxLayout(diag_panel)
        diag_l.setContentsMargins(14, 14, 14, 14)
        diag_l.setSpacing(10)

        diag_title = QLabel("BMS DIAGNOSTIC")
        diag_title.setStyleSheet("color: cyan; font-family:Orbitron; font-size:11px;")
        diag_l.addWidget(diag_title)

        self.lbl_mask = QLabel("STATUS: 0x0000")
        self.lbl_mask.setStyleSheet("color:#DDD; font-family:Orbitron; font-size:14px; font-weight:bold;")
        diag_l.addWidget(self.lbl_mask)

        self.al_ov = AlertLamp("OV (Overvoltage)")
        self.al_ot = AlertLamp("OT (Overtemp)")
        self.al_sc = AlertLamp("SC (Short-circuit)")
        diag_l.addWidget(self.al_ov)
        diag_l.addWidget(self.al_ot)
        diag_l.addWidget(self.al_sc)
        diag_l.addStretch(1)

        right.addWidget(mos_panel)
        right.addWidget(diag_panel)
        right.addStretch(1)

        content.addLayout(right)

        root.addLayout(content, 1)

    def resizeEvent(self, event):
        # Overlay plein écran
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(self.rect())
        super().resizeEvent(event)

    def show_overlay(self) -> None:
        self.overlay.show()
        self.overlay.raise_()

    # -----------------
    # Signals
    # -----------------
    def _connect_signals(self) -> None:
        self.store.pack_voltage_changed.connect(self._on_vpack)
        self.store.cell_min_v.connect(self._on_vmin)
        self.store.cell_max_v.connect(self._on_vmax)
        self.store.cell_delta_v.connect(self._on_delta)
        self.store.cell_voltages_changed.connect(self._on_cells)

        self.store.mosfet_status_changed.connect(self._on_mosfets)
        self.store.bms_status_bitmask.connect(self._on_bitmask)

    @Slot(float)
    def _on_vpack(self, v: float):
        self._vpack = float(v)
        self._refresh_card()

    @Slot(float)
    def _on_vmin(self, v: float):
        self._vmin = float(v)
        self._refresh_card()

    @Slot(float)
    def _on_vmax(self, v: float):
        self._vmax = float(v)
        self._refresh_card()

    @Slot(float)
    def _on_delta(self, v: float):
        self._delta = float(v)
        self._refresh_card()

    @Slot(list)
    def _on_cells(self, v_list):
        for i, v in enumerate(v_list):
            if i < 16:
                self.cell_widgets[i].set_voltage(v)

    @Slot(bool, bool)
    def _on_mosfets(self, charge_on: bool, discharge_on: bool):
        self.lamp_charge.set_on(charge_on, color_on="#00FFD0")
        self.lamp_discharge.set_on(discharge_on, color_on="#00FFD0")

    @Slot(int)
    def _on_bitmask(self, mask: int):
        self._bitmask = int(mask) & 0xFFFF
        self.lbl_mask.setText(f"STATUS: 0x{self._bitmask:04X}")

        self.al_ov.set_alert(bool(self._bitmask & self.BIT_OV))
        self.al_ot.set_alert(bool(self._bitmask & self.BIT_OT))
        self.al_sc.set_alert(bool(self._bitmask & self.BIT_SC))

    def _refresh_card(self) -> None:
        self.card.update_data(self._vpack, self._delta, self._vmin, self._vmax)
