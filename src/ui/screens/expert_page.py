from __future__ import annotations

from qtpy.QtCore import Qt, Slot, QEvent
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
    """Lampe ON/OFF stylée par QSS via properties (state/kind)."""

    def __init__(self, title: str, parent=None, kind: str | None = None):
        super().__init__(parent)
        self._on = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(34)

        self.setObjectName("StatusLamp")
        if kind:
            self.setProperty("kind", kind)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setObjectName("LampDot")
        layout.addWidget(self.dot)

        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("LampLabel")
        layout.addWidget(self.lbl_title)

        layout.addStretch(1)

        self.badge = QLabel("OFF")
        self.badge.setFixedSize(44, 22)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setObjectName("LampBadge")
        layout.addWidget(self.badge)

        self.set_on(False)

    def set_on(self, state: bool) -> None:
        self._on = bool(state)
        self.setProperty("state", "on" if self._on else "off")
        self.badge.setText("ON" if self._on else "OFF")

        # Force QSS refresh when dynamic properties change
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class AlertLamp(Lamp):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent, kind="danger")

    def set_alert(self, state: bool) -> None:
        self.set_on(state)


class ExpertPage(QWidget):
    # Bits diagnostics (placeholder -> ajuste si table JK diffère)
    BIT_OV = 0x0004
    BIT_OT = 0x0008
    BIT_SC = 0x0010

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._vpack = 0.0
        self._current = 0.0
        self._power_kw = 0.0
        self._vmin = 0.0
        self._vmax = 0.0
        self._delta = 0.0
        self._t1 = 0.0
        self._t2 = 0.0
        self._tmos = 0.0
        self._soc = 0
        self._cap_ah = 0.0
        self._cycles = 0
        self._charge_on = False
        self._discharge_on = False
        self._overlay_host = None
        self._host_filter_installed = False

        self._build_main()
        self._build_overlay()
        self._connect_signals()

    # -----------------
    # UI helpers
    # -----------------
    def _make_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setObjectName("Card")

        v = QVBoxLayout(card)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(8)

        t = QLabel(title)
        t.setObjectName("CardTitle")
        v.addWidget(t)

        return card, v

    def _kv(self, key: str, initial: str = "--") -> tuple[QHBoxLayout, QLabel]:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        k = QLabel(key)
        k.setObjectName("Muted")

        val = QLabel(initial)
        val.setObjectName("Value")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setMinimumWidth(90)

        row.addWidget(k)
        row.addStretch(1)
        row.addWidget(val)
        return row, val

    # -----------------
    # Main page
    # -----------------
    def _build_main(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(12)

        # Left: BMS HEALTH (tap -> overlay)
        self.card_bms = BMSSummaryCard(self)
        self.card_bms.clicked.connect(self.show_overlay)
        top.addWidget(self.card_bms)

        # Right column: CHARGEUR + BMS STATS
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        # --- Charger card ---
        self.charger_card, charger_l = self._make_card("CHARGEUR")

        lamp_row = QHBoxLayout()
        lamp_row.setSpacing(10)
        self.lamp_charge_main = Lamp("MOS CHARGE")
        self.lamp_discharge_main = Lamp("MOS DISCH")
        lamp_row.addWidget(self.lamp_charge_main, 1)
        lamp_row.addWidget(self.lamp_discharge_main, 1)
        charger_l.addLayout(lamp_row)

        row, self.val_vbat_main = self._kv("Vbat", "--.- V")
        charger_l.addLayout(row)
        row, self.val_ibat_main = self._kv("Ibat", "--.- A")
        charger_l.addLayout(row)
        row, self.val_p_main = self._kv("P", "--.- kW")
        charger_l.addLayout(row)

        self.lbl_charge_mode = QLabel("—")
        self.lbl_charge_mode.setObjectName("Hint")
        charger_l.addWidget(self.lbl_charge_mode)

        right_col.addWidget(self.charger_card)

        # --- BMS stats / diag card ---
        self.stats_card, stats_l = self._make_card("BMS STATS / DIAG")

        row, self.val_soc = self._kv("SOC", "-- %")
        stats_l.addLayout(row)
        row, self.val_cap = self._kv("Restant", "--.- Ah")
        stats_l.addLayout(row)
        row, self.val_cycles = self._kv("Cycles", "--")
        stats_l.addLayout(row)

        self.lbl_mask_main = QLabel("STATUS: 0x0000")
        self.lbl_mask_main.setObjectName("Value")
        stats_l.addWidget(self.lbl_mask_main)

        self.al_ov_main = AlertLamp("OV (Overvoltage)")
        self.al_ot_main = AlertLamp("OT (Overtemp)")
        self.al_sc_main = AlertLamp("SC (Short-circuit)")
        stats_l.addWidget(self.al_ov_main)
        stats_l.addWidget(self.al_ot_main)
        stats_l.addWidget(self.al_sc_main)

        right_col.addWidget(self.stats_card)
        right_col.addStretch(1)

        top.addLayout(right_col, 1)
        root.addLayout(top, 1)

    # -----------------
    # Overlay (cells + controls)
    # -----------------
    def _build_overlay(self) -> None:
        self.overlay = QFrame(self)
        self.overlay.hide()
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.overlay.setObjectName("Overlay")

        root = QVBoxLayout(self.overlay)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(8)

        # Header
        header = QFrame(self.overlay)
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setObjectName("Card")
        header.setFixedHeight(40)

        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 6, 12, 6)
        hl.setSpacing(10)

        title = QLabel("FULL BMS CONTROL")
        title.setObjectName("CardTitle")
        hl.addWidget(title)

        hl.addStretch(1)

        self.btn_close = QPushButton("CLOSE")
        self.btn_close.setFixedSize(90, 28)
        self.btn_close.clicked.connect(self.hide_overlay)
        hl.addWidget(self.btn_close)

        root.addWidget(header)

        content = QHBoxLayout()
        content.setSpacing(10)

        # Cells grid
        grid_wrap = QFrame(self.overlay)
        grid_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        grid_wrap.setObjectName("Card")

        grid_layout = QVBoxLayout(grid_wrap)
        grid_layout.setContentsMargins(12, 10, 12, 10)
        grid_layout.setSpacing(8)

        lbl_cells = QLabel("CELLS")
        lbl_cells.setObjectName("Muted")
        grid_layout.addWidget(lbl_cells)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i + 1, grid_wrap)
            self.cell_widgets.append(icon)
            grid.addWidget(icon, i // 4, i % 4, Qt.AlignmentFlag.AlignCenter)

        grid_layout.addLayout(grid, 1)
        content.addWidget(grid_wrap, 1)

        # Right column in overlay
        right = QVBoxLayout()
        right.setSpacing(10)

        def make_panel(title_text: str) -> tuple[QFrame, QVBoxLayout]:
            panel, v = self._make_card(title_text)
            return panel, v

        # MOSFET STATUS + manual toggles
        mos_panel, mos_l = make_panel("MOSFET STATUS")
        self.lamp_charge = Lamp("CHARGE")
        self.lamp_discharge = Lamp("DISCHARGE")
        mos_l.addWidget(self.lamp_charge)
        mos_l.addWidget(self.lamp_discharge)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_charge_toggle = QPushButton("TOGGLE CHARGE")
        self.btn_charge_toggle.setFixedHeight(30)
        self.btn_charge_toggle.clicked.connect(self._toggle_charge_mos)
        btn_row.addWidget(self.btn_charge_toggle)

        self.btn_discharge_toggle = QPushButton("TOGGLE DISCH")
        self.btn_discharge_toggle.setFixedHeight(30)
        self.btn_discharge_toggle.setProperty("variant", "danger")
        self.btn_discharge_toggle.clicked.connect(self._toggle_discharge_mos)
        btn_row.addWidget(self.btn_discharge_toggle)

        mos_l.addLayout(btn_row)
        right.addWidget(mos_panel)

        # REAL-TIME DATA
        rt_panel, rt_l = make_panel("REAL-TIME DATA")
        row, self.val_current = self._kv("Courant", "0.0 A")
        rt_l.addLayout(row)
        row, self.val_power = self._kv("Puissance", "0.0 kW")
        rt_l.addLayout(row)
        row, self.val_t1 = self._kv("Temp Sonde 1", "0 °C")
        rt_l.addLayout(row)
        row, self.val_t2 = self._kv("Temp Sonde 2", "0 °C")
        rt_l.addLayout(row)
        row, self.val_tmos = self._kv("Temp MOSFET", "0 °C")
        rt_l.addLayout(row)
        right.addWidget(rt_panel)

        # BMS DIAGNOSTIC
        diag_panel, diag_l = make_panel("BMS DIAGNOSTIC")
        self.lbl_mask = QLabel("STATUS: 0x0000")
        self.lbl_mask.setObjectName("Value")
        diag_l.addWidget(self.lbl_mask)
        self.al_ov = AlertLamp("OV (Overvoltage)")
        self.al_ot = AlertLamp("OT (Overtemp)")
        self.al_sc = AlertLamp("SC (Short-circuit)")
        diag_l.addWidget(self.al_ov)
        diag_l.addWidget(self.al_ot)
        diag_l.addWidget(self.al_sc)
        right.addWidget(diag_panel)

        right.addStretch(1)
        content.addLayout(right, 1)

        root.addLayout(content, 1)

    # -----------------
    # Overlay geometry
    # -----------------
    def _ensure_overlay_host(self) -> None:
        host = self.window()
        if host is None:
            return
        if self._overlay_host is not host:
            self._overlay_host = host
            if self.overlay.parentWidget() is not host:
                self.overlay.setParent(host)
            self.overlay.raise_()

            if not self._host_filter_installed:
                host.installEventFilter(self)
                self._host_filter_installed = True

            self._sync_overlay_geometry()

    def _sync_overlay_geometry(self) -> None:
        if self._overlay_host is None:
            return
        self.overlay.setGeometry(self._overlay_host.rect())

    def eventFilter(self, obj, event):
        if obj is self._overlay_host and event.type() == QEvent.Type.Resize:
            if self.overlay.isVisible():
                self._sync_overlay_geometry()
        return super().eventFilter(obj, event)

    def show_overlay(self) -> None:
        self._ensure_overlay_host()
        self.overlay.show()
        self.overlay.raise_()

    def hide_overlay(self) -> None:
        self.overlay.hide()

    # -----------------
    # Manual MOSFET control
    # -----------------
    def _toggle_charge_mos(self) -> None:
        self.store.request_set_charge_mosfet(not self._charge_on)

    def _toggle_discharge_mos(self) -> None:
        self.store.request_set_discharge_mosfet(not self._discharge_on)

    # -----------------
    # Signals
    # -----------------
    def _connect_signals(self) -> None:
        self.store.pack_voltage_changed.connect(self._on_vpack)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.cell_min_v.connect(self._on_vmin)
        self.store.cell_max_v.connect(self._on_vmax)
        self.store.cell_delta_v.connect(self._on_delta)
        self.store.cell_voltages_changed.connect(self._on_cells)
        self.store.mosfet_status_changed.connect(self._on_mosfets)
        self.store.bms_status_bitmask.connect(self._on_bitmask)

        # Optional JK tech
        if hasattr(self.store, "soc_changed"):
            self.store.soc_changed.connect(self._on_soc)
        if hasattr(self.store, "capacity_remaining_ah"):
            self.store.capacity_remaining_ah.connect(self._on_cap)
        if hasattr(self.store, "cycle_count"):
            self.store.cycle_count.connect(self._on_cycles)

        if hasattr(self.store, "temp_sensor_1_changed"):
            self.store.temp_sensor_1_changed.connect(self._on_t1)
        if hasattr(self.store, "temp_sensor_2_changed"):
            self.store.temp_sensor_2_changed.connect(self._on_t2)
        if hasattr(self.store, "temp_mosfet_changed"):
            self.store.temp_mosfet_changed.connect(self._on_tmos)

    def _refresh_charger_block(self) -> None:
        self.val_vbat_main.setText(f"{self._vpack:.1f} V")
        self.val_ibat_main.setText(f"{self._current:.1f} A")
        self.val_p_main.setText(f"{self._power_kw:.1f} kW")

        if abs(self._current) < 0.5:
            self.lbl_charge_mode.setText("IDLE")
        elif self._current < 0:
            self.lbl_charge_mode.setText("CHARGING (Ibat < 0)")
        else:
            self.lbl_charge_mode.setText("DISCHARGING (Ibat > 0)")

    def _refresh_card(self) -> None:
        self.card_bms.update_data(self._vpack, self._delta, self._vmin, self._vmax)

    def _recalc_power(self) -> None:
        self._power_kw = (self._vpack * self._current) / 1000.0
        self.val_current.setText(f"{self._current:.1f} A")
        self.val_power.setText(f"{self._power_kw:.1f} kW")
        self._refresh_charger_block()

    @Slot(float)
    def _on_vpack(self, v: float):
        self._vpack = float(v)
        self._recalc_power()
        self._refresh_card()

    @Slot(float)
    def _on_current(self, a: float):
        self._current = float(a)
        self._recalc_power()

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
        self._charge_on = bool(charge_on)
        self._discharge_on = bool(discharge_on)

        # Main page
        self.lamp_charge_main.set_on(self._charge_on)
        self.lamp_discharge_main.set_on(self._discharge_on)

        # Overlay
        self.lamp_charge.set_on(self._charge_on)
        self.lamp_discharge.set_on(self._discharge_on)

    @Slot(int)
    def _on_bitmask(self, mask: int):
        bm = int(mask) & 0xFFFF

        self.lbl_mask.setText(f"STATUS: 0x{bm:04X}")
        self.lbl_mask_main.setText(f"STATUS: 0x{bm:04X}")

        ov = bool(bm & self.BIT_OV)
        ot = bool(bm & self.BIT_OT)
        sc = bool(bm & self.BIT_SC)

        self.al_ov.set_alert(ov)
        self.al_ot.set_alert(ot)
        self.al_sc.set_alert(sc)

        self.al_ov_main.set_alert(ov)
        self.al_ot_main.set_alert(ot)
        self.al_sc_main.set_alert(sc)

    @Slot(int)
    def _on_soc(self, soc: int):
        self._soc = int(soc)
        self.val_soc.setText(f"{self._soc:d} %")

    @Slot(float)
    def _on_cap(self, ah: float):
        self._cap_ah = float(ah)
        self.val_cap.setText(f"{self._cap_ah:.1f} Ah")

    @Slot(int)
    def _on_cycles(self, c: int):
        self._cycles = int(c)
        self.val_cycles.setText(f"{self._cycles:d}")

    @Slot(float)
    def _on_t1(self, t: float):
        self._t1 = float(t)
        self.val_t1.setText(f"{self._t1:.0f} °C")

    @Slot(float)
    def _on_t2(self, t: float):
        self._t2 = float(t)
        self.val_t2.setText(f"{self._t2:.0f} °C")

    @Slot(float)
    def _on_tmos(self, t: float):
        self._tmos = float(t)
        self.val_tmos.setText(f"{self._tmos:.0f} °C")