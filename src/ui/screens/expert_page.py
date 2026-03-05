from __future__ import annotations

from qtpy.QtCore import Qt, Slot, QEvent, QTimer
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


class LedIndicator(QFrame):
    """
    Petite LED style "face avant chargeur".
    state: 0=OFF, 1=ON, 2=BLINK
    """
    OFF = 0
    ON = 1
    BLINK = 2

    def __init__(self, name: str, *, color_on: str, color_blink: str, parent=None):
        super().__init__(parent)
        self._state = self.OFF
        self._blink_phase = False
        self._color_on = color_on
        self._color_blink = color_blink

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QFrame { background: transparent; }")

        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        self.dot = QLabel("●")
        self.dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dot.setStyleSheet("color:#222; font-size:16px;")
        l.addWidget(self.dot)

        self.lbl = QLabel(name)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:8px;")
        l.addWidget(self.lbl)

        self._timer = QTimer(self)
        self._timer.setInterval(450)
        self._timer.timeout.connect(self._on_blink_tick)

    @staticmethod
    def _clamp(state: int) -> int:
        try:
            v = int(state)
        except Exception:
            v = 0
        return 0 if v < 0 else 2 if v > 2 else v

    def set_state(self, state: int) -> None:
        s = self._clamp(state)
        if s == self._state:
            return
        self._state = s
        self._blink_phase = False

        if self._state == self.BLINK:
            self._timer.start()
        else:
            self._timer.stop()
        self._apply()

    def _on_blink_tick(self) -> None:
        if self._state != self.BLINK:
            self._timer.stop()
            return
        self._blink_phase = not self._blink_phase
        self._apply()

    def _apply(self) -> None:
        if self._state == self.ON:
            self.dot.setStyleSheet(f"color:{self._color_on}; font-size:16px;")
            return

        if self._state == self.BLINK:
            # alterne entre ON et OFF visuellement
            if self._blink_phase:
                self.dot.setStyleSheet(f"color:{self._color_blink}; font-size:16px;")
            else:
                self.dot.setStyleSheet("color:#222; font-size:16px;")
            return

        self.dot.setStyleSheet("color:#222; font-size:16px;")


class Lamp(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._on = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(34)
        self.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:12px; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setStyleSheet("color:#222; font-size:14px;")
        layout.addWidget(self.dot)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:9px;")
        layout.addWidget(self.lbl_title)

        layout.addStretch(1)

        self.badge = QLabel("OFF")
        self.badge.setFixedSize(44, 22)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setStyleSheet(
            "background:#111; border:1px solid #222; border-radius:10px; "
            "color:#666; font-family:Orbitron; font-weight:bold; font-size:9px;"
        )
        layout.addWidget(self.badge)

    def set_on(self, state: bool, color_on: str = "#00FFD0") -> None:
        self._on = bool(state)
        if self._on:
            self.dot.setStyleSheet(f"color:{color_on}; font-size:14px;")
            self.badge.setText("ON")
            self.badge.setStyleSheet(
                f"background:{color_on}; border:none; border-radius:10px; "
                "color:#000; font-family:Orbitron; font-weight:bold; font-size:9px;"
            )
        else:
            self.dot.setStyleSheet("color:#222; font-size:14px;")
            self.badge.setText("OFF")
            self.badge.setStyleSheet(
                "background:#111; border:1px solid #222; border-radius:10px; "
                "color:#666; font-family:Orbitron; font-weight:bold; font-size:9px;"
            )


class AlertLamp(Lamp):
    def set_alert(self, state: bool) -> None:
        super().set_on(state, color_on="#FF4040")


class ExpertPage(QWidget):
    # Bits diagnostics (placeholder -> ajuste si table JK diffère)
    BIT_OV = 0x0004
    BIT_OT = 0x0008
    BIT_SC = 0x0010

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self._vpack = 0.0
        self._current = 0.0
        self._power_kw = 0.0

        self._vmin = 0.0
        self._vmax = 0.0
        self._delta = 0.0

        self._t1 = 0.0
        self._t2 = 0.0
        self._tmos = 0.0

        self._charge_on = False
        self._discharge_on = False

        self._overlay_host = None
        self._host_filter_installed = False

        # Charger LED state cache
        self._charger_plugged = False

        self._build_main()
        self._build_overlay()
        self._connect_signals()

    # -----------------
    # MAIN SCREEN (card + charger box)
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

        # ---- Charger box (ici, pas dans l'overlay BMS)
        self.charger_box = QFrame(self)
        self.charger_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.charger_box.setStyleSheet("QFrame { background:#060606; border:1px solid #222; border-radius:16px; }")

        cb = QVBoxLayout(self.charger_box)
        cb.setContentsMargins(14, 12, 14, 12)
        cb.setSpacing(10)

        title = QLabel("CHARGER (SKYLLA TG)")
        title.setStyleSheet("color: cyan; font-family: Orbitron; font-size: 11px; font-weight: bold;")
        cb.addWidget(title)

        self.lbl_plug = QLabel("PLUG: --")
        self.lbl_plug.setStyleSheet("color:#777; font-family:Orbitron; font-size:9px; font-weight:bold;")
        cb.addWidget(self.lbl_plug)

        leds = QHBoxLayout()
        leds.setSpacing(14)

        self.led_on = LedIndicator("ON", color_on="#00FFD0", color_blink="#FFC000")
        self.led_boost = LedIndicator("BOOST", color_on="#00FFD0", color_blink="#FFC000")
        self.led_equalize = LedIndicator("EQUALIZE", color_on="#00FFD0", color_blink="#FFC000")
        self.led_float = LedIndicator("FLOAT", color_on="#00FFD0", color_blink="#FFC000")
        self.led_failure = LedIndicator("FAILURE", color_on="#FF4040", color_blink="#FF4040")

        leds.addWidget(self.led_on)
        leds.addWidget(self.led_boost)
        leds.addWidget(self.led_equalize)
        leds.addWidget(self.led_float)
        leds.addWidget(self.led_failure)
        leds.addStretch(1)

        cb.addLayout(leds)

        vals = QHBoxLayout()
        vals.setSpacing(10)

        k1 = QLabel("VBAT")
        k1.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:9px;")
        self.lbl_vbat = QLabel("--.- V")
        self.lbl_vbat.setStyleSheet("color:#EEE; font-family:Orbitron; font-size:12px; font-weight:bold;")

        k2 = QLabel("IBAT")
        k2.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:9px;")
        self.lbl_ibat = QLabel("--.- A")
        self.lbl_ibat.setStyleSheet("color:#EEE; font-family:Orbitron; font-size:12px; font-weight:bold;")

        vals.addWidget(k1)
        vals.addWidget(self.lbl_vbat)
        vals.addSpacing(18)
        vals.addWidget(k2)
        vals.addWidget(self.lbl_ibat)
        vals.addStretch(1)

        cb.addLayout(vals)

        row.addWidget(self.charger_box, 1)

        layout.addLayout(row)
        layout.addStretch(1)

    # -----------------
    # OVERLAY BMS (cells, mosfets, diag) - inchangé
    # -----------------
    def _build_overlay(self) -> None:
        self.overlay = QFrame(self)
        self.overlay.hide()
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.overlay.setStyleSheet("QFrame { background-color: rgba(0, 0, 0, 250); border:none; }")

        root = QVBoxLayout(self.overlay)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(6)

        header = QFrame(self.overlay)
        header.setFixedHeight(34)
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:12px; }")

        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 4, 10, 4)
        hl.setSpacing(8)

        title = QLabel("FULL BMS CONTROL")
        title.setStyleSheet("color: cyan; font-family: Orbitron; font-size: 12px; font-weight: bold;")
        hl.addWidget(title)
        hl.addStretch(1)

        self.btn_close = QPushButton("CLOSE")
        self.btn_close.setFixedSize(78, 24)
        self.btn_close.setStyleSheet(
            "QPushButton { background:#111; color:#DDD; border:1px solid #222; border-radius:10px; "
            "font-family:Orbitron; font-weight:bold; font-size:9px; }"
            "QPushButton:pressed { background:#00FFD0; color:#000; border:none; }"
        )
        self.btn_close.clicked.connect(self.hide_overlay)
        hl.addWidget(self.btn_close)

        root.addWidget(header)

        content = QHBoxLayout()
        content.setSpacing(8)

        # Cells grid
        grid_wrap = QFrame(self.overlay)
        grid_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        grid_wrap.setStyleSheet("QFrame { background:#050505; border:1px solid #222; border-radius:14px; }")

        grid_layout = QVBoxLayout(grid_wrap)
        grid_layout.setContentsMargins(10, 8, 10, 8)
        grid_layout.setSpacing(4)

        lbl_cells = QLabel("CELLS")
        lbl_cells.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:10px;")
        grid_layout.addWidget(lbl_cells)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i + 1, grid_wrap)
            self.cell_widgets.append(icon)
            grid.addWidget(icon, i // 4, i % 4, Qt.AlignmentFlag.AlignCenter)

        grid_layout.addLayout(grid, 1)
        content.addWidget(grid_wrap, 1)

        # Right column
        right = QVBoxLayout()
        right.setSpacing(6)

        def make_panel(title_text: str) -> tuple[QFrame, QVBoxLayout]:
            panel = QFrame(self.overlay)
            panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            panel.setStyleSheet("QFrame { background:#0A0A0A; border:1px solid #222; border-radius:14px; }")
            v = QVBoxLayout(panel)
            v.setContentsMargins(10, 8, 10, 8)
            v.setSpacing(4)
            t = QLabel(title_text)
            t.setStyleSheet("color: cyan; font-family:Orbitron; font-size:10px;")
            v.addWidget(t)
            return panel, v

        # MOSFET STATUS
        mos_panel, mos_l = make_panel("MOSFET STATUS")
        self.lamp_charge = Lamp("CHARGE")
        self.lamp_discharge = Lamp("DISCHARGE")
        mos_l.addWidget(self.lamp_charge)
        mos_l.addWidget(self.lamp_discharge)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_charge_toggle = QPushButton("TOGGLE CHARGE")
        self.btn_charge_toggle.setFixedHeight(26)
        self.btn_charge_toggle.setStyleSheet(
            "QPushButton { background:#111; color:#DDD; border:1px solid #222; border-radius:10px; "
            "font-family:Orbitron; font-weight:bold; font-size:9px; padding:0 8px; }"
            "QPushButton:pressed { background:#00FFD0; color:#000; border:none; }"
        )
        self.btn_charge_toggle.clicked.connect(self._toggle_charge_mos)
        btn_row.addWidget(self.btn_charge_toggle)

        self.btn_discharge_toggle = QPushButton("TOGGLE DISCH")
        self.btn_discharge_toggle.setFixedHeight(26)
        self.btn_discharge_toggle.setStyleSheet(
            "QPushButton { background:#111; color:#DDD; border:1px solid #222; border-radius:10px; "
            "font-family:Orbitron; font-weight:bold; font-size:9px; padding:0 8px; }"
            "QPushButton:pressed { background:#FF4040; color:#000; border:none; }"
        )
        self.btn_discharge_toggle.clicked.connect(self._toggle_discharge_mos)
        btn_row.addWidget(self.btn_discharge_toggle)

        mos_l.addLayout(btn_row)
        right.addWidget(mos_panel)

        # REAL-TIME DATA
        rt_panel, rt_l = make_panel("REAL-TIME DATA")

        def make_kv_row(label: str, initial: str) -> QLabel:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)

            k = QLabel(label)
            k.setStyleSheet("color:#AAA; font-family:Orbitron; font-size:9px;")

            v = QLabel(initial)
            v.setMinimumWidth(70)
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            v.setStyleSheet("color:#EEE; font-family:Orbitron; font-size:10px; font-weight:bold;")

            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(v)
            rt_l.addLayout(row)
            return v

        self.val_current = make_kv_row("Courant", "0.0 A")
        self.val_power = make_kv_row("Puissance", "0.0 kW")
        self.val_t1 = make_kv_row("Temp Sonde 1", "0 °C")
        self.val_t2 = make_kv_row("Temp Sonde 2", "0 °C")
        self.val_tmos = make_kv_row("Temp MOSFET", "0 °C")
        right.addWidget(rt_panel)

        # BMS DIAGNOSTIC
        diag_panel, diag_l = make_panel("BMS DIAGNOSTIC")
        self.lbl_mask = QLabel("STATUS: 0x0000")
        self.lbl_mask.setStyleSheet("color:#DDD; font-family:Orbitron; font-size:11px; font-weight:bold;")
        diag_l.addWidget(self.lbl_mask)

        self.al_ov = AlertLamp("OV (Overvoltage)")
        self.al_ot = AlertLamp("OT (Overtemp)")
        self.al_sc = AlertLamp("SC (Short-circuit)")
        diag_l.addWidget(self.al_ov)
        diag_l.addWidget(self.al_ot)
        diag_l.addWidget(self.al_sc)

        right.addWidget(diag_panel)
        right.addStretch(1)

        content.addLayout(right)
        root.addLayout(content, 1)

    # -----------------
    # Overlay sizing on window()
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
    # Manual toggle handlers
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

        if hasattr(self.store, "temp_sensor_1_changed"):
            self.store.temp_sensor_1_changed.connect(self._on_t1)
        if hasattr(self.store, "temp_sensor_2_changed"):
            self.store.temp_sensor_2_changed.connect(self._on_t2)
        if hasattr(self.store, "temp_mosfet_changed"):
            self.store.temp_mosfet_changed.connect(self._on_tmos)

        # Charger (simu pour l'instant)
        if hasattr(self.store, "charger_connected_changed"):
            self.store.charger_connected_changed.connect(self._on_charger_connected)
        if hasattr(self.store, "charger_leds_changed"):
            self.store.charger_leds_changed.connect(self._on_charger_leds)

    @Slot(float)
    def _on_vpack(self, v: float):
        self._vpack = float(v)
        self._recalc_power()
        self._refresh_card()
        self.lbl_vbat.setText(f"{self._vpack:.1f} V")

    @Slot(float)
    def _on_current(self, a: float):
        self._current = float(a)
        self._recalc_power()
        self.lbl_ibat.setText(f"{self._current:.1f} A")

    def _recalc_power(self):
        self._power_kw = (self._vpack * self._current) / 1000.0
        self.val_current.setText(f"{self._current:.1f} A")
        self.val_power.setText(f"{self._power_kw:.1f} kW")

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
        self.lamp_charge.set_on(self._charge_on, color_on="#00FFD0")
        self.lamp_discharge.set_on(self._discharge_on, color_on="#00FFD0")

    @Slot(int)
    def _on_bitmask(self, mask: int):
        bm = int(mask) & 0xFFFF
        self.lbl_mask.setText(f"STATUS: 0x{bm:04X}")
        self.al_ov.set_alert(bool(bm & self.BIT_OV))
        self.al_ot.set_alert(bool(bm & self.BIT_OT))
        self.al_sc.set_alert(bool(bm & self.BIT_SC))

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

    @Slot(bool)
    def _on_charger_connected(self, plugged: bool) -> None:
        self._charger_plugged = bool(plugged)
        if self._charger_plugged:
            self.lbl_plug.setText("PLUG: YES")
            self.lbl_plug.setStyleSheet("color:#00FFD0; font-family:Orbitron; font-size:9px; font-weight:bold;")
        else:
            self.lbl_plug.setText("PLUG: NO")
            self.lbl_plug.setStyleSheet("color:#777; font-family:Orbitron; font-size:9px; font-weight:bold;")
            # reset LEDs
            self.led_on.set_state(0)
            self.led_boost.set_state(0)
            self.led_equalize.set_state(0)
            self.led_float.set_state(0)
            self.led_failure.set_state(0)

    @Slot(int, int, int, int, int)
    def _on_charger_leds(self, on: int, boost: int, equalize: int, float_: int, failure: int) -> None:
        self.led_on.set_state(on)
        self.led_boost.set_state(boost)
        self.led_equalize.set_state(equalize)
        self.led_float.set_state(float_)
        self.led_failure.set_state(failure)

    def _refresh_card(self) -> None:
        self.card.update_data(self._vpack, self._delta, self._vmin, self._vmax)