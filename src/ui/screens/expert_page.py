from __future__ import annotations

from qtpy.QtCore import QEvent, Qt, Slot
from qtpy.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.ui.components.battery_elements import BMSSummaryCard, BatteryIcon


class Lamp(QFrame):
    def __init__(self, title: str, parent=None, kind: str | None = None):
        super().__init__(parent)
        self._on = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(30)
        self.setObjectName("StatusLamp")
        if kind:
            self.setProperty("kind", kind)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self.dot = QLabel("●")
        layout.addWidget(self.dot)

        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("LampLabel")
        self.lbl_title.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.lbl_title)

        layout.addStretch(1)

        self.badge = QLabel("OFF")
        self.badge.setFixedSize(48, 20)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.badge)

        self.set_on(False)

    def set_on(self, state: bool) -> None:
        self._on = bool(state)
        self.badge.setText("ON" if self._on else "OFF")

        if self._on:
            dot_color = "#22c55e"
            badge_bg = "#12351f"
            badge_fg = "#9df5b5"
            border = "#2b6d40"
        else:
            dot_color = "#555555"
            badge_bg = "#1e1e1e"
            badge_fg = "#8a8a8a"
            border = "#3a3a3a"

        self.dot.setStyleSheet(f"color: {dot_color}; font-size: 15px;")
        self.badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {badge_bg};
                color: {badge_fg};
                border: 1px solid {border};
                border-radius: 5px;
                font-weight: 700;
                font-size: 10px;
                padding: 0 3px;
            }}
            """
        )
        self.update()


class AlertLamp(Lamp):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent, kind="danger")

    def set_alert(self, state: bool) -> None:
        self.set_on(state)


class LedPill(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("StatusLamp")
        self.setFixedHeight(21)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(4)

        self.dot = QLabel("●")
        layout.addWidget(self.dot)

        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("LampLabel")
        self.lbl_title.setStyleSheet("font-size: 9px;")
        layout.addWidget(self.lbl_title)

        layout.addStretch(1)

        self.badge = QLabel("OFF")
        self.badge.setFixedSize(38, 14)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.badge)

        self.set_state(0)

    def set_state(self, state: int) -> None:
        try:
            state = int(state)
        except Exception:
            state = 0

        state = 0 if state < 0 else 2 if state > 2 else state

        if state == 0:
            text = "OFF"
            dot_color = "#555555"
            badge_bg = "#1e1e1e"
            badge_fg = "#8a8a8a"
            border = "#3a3a3a"
        elif state == 1:
            text = "ON"
            dot_color = "#22c55e"
            badge_bg = "#12351f"
            badge_fg = "#9df5b5"
            border = "#2b6d40"
        else:
            text = "BLINK"
            dot_color = "#f59e0b"
            badge_bg = "#3a2a08"
            badge_fg = "#ffd27a"
            border = "#8b6914"

        self.badge.setText(text)
        self.dot.setStyleSheet(f"color: {dot_color}; font-size: 11px;")
        self.badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {badge_bg};
                color: {badge_fg};
                border: 1px solid {border};
                border-radius: 4px;
                font-size: 8px;
                font-weight: 700;
                padding: 0 2px;
            }}
            """
        )
        self.update()


class ExpertPage(QWidget):
    BIT_OV = 0x0004
    BIT_OT = 0x0008
    BIT_SC = 0x0010

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.variator = getattr(store, "variator_service", None)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._vpack = 0.0
        self._current = 0.0
        self._power_kw = 0.0
        self._traction_kw = 0.0
        self._charge_kw = 0.0
        self._vmin = 0.0
        self._vmax = 0.0
        self._delta = 0.0
        self._t1 = 0.0
        self._t2 = 0.0
        self._tmos = 0.0
        self._soc = 0
        self._cap_ah = 0.0
        self._cycles = 0
        self._bitmask = 0
        self._charge_on = False
        self._discharge_on = False

        self._charger_connected = False
        self._charger_led_on = 0
        self._charger_led_boost = 0
        self._charger_led_equalize = 0
        self._charger_led_float = 0
        self._charger_led_failure = 0
        self._charger_leds_seen = False

        self._variator_connected = False
        self._variator_speed = 0.0
        self._variator_mode = 0
        self._variator_brake = False
        self._selected_mode = 0

        self._borne_state = "OFFLINE"
        self._borne_current_limit = 0
        self._borne_cable_limit = 0
        self._borne_cp_duty = 0.0
        self._borne_cp_freq = 0.0
        self._borne_cp_neg = -12.0
        self._borne_pp_voltage = 0.0
        self._borne_sector_present = False
        self._borne_cp_ok = False

        self._overlay_host = None
        self._host_filter_installed = False

        self._build_main()
        self._build_overlay()
        self._connect_signals()
        self._refresh_bms_card()
        self._refresh_bms_overlay()
        self._refresh_charger_card()
        self._refresh_variator_card()
        self._refresh_borne_card()

    def _make_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setObjectName("Card")

        v = QVBoxLayout(card)
        v.setContentsMargins(9, 7, 9, 7)
        v.setSpacing(5)

        t = QLabel(title)
        t.setObjectName("CardTitle")
        t.setStyleSheet("font-size: 11px;")
        v.addWidget(t)

        return card, v

    def _kv(self, key: str, initial: str = "--") -> tuple[QHBoxLayout, QLabel]:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)

        k = QLabel(key)
        k.setObjectName("Muted")
        k.setStyleSheet("font-size: 9px;")

        val = QLabel(initial)
        val.setObjectName("Value")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setMinimumWidth(76)
        val.setStyleSheet("font-size: 10px;")

        row.addWidget(k)
        row.addStretch(1)
        row.addWidget(val)
        return row, val

    def _build_main(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 8)
        root.setSpacing(7)

        main_cols = QHBoxLayout()
        main_cols.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        self.card_bms = BMSSummaryCard(self)
        self.card_bms.clicked.connect(self.show_overlay)
        self.card_bms.setMinimumHeight(170)
        left_col.addWidget(self.card_bms, 4)

        self.variator_card, var_l = self._make_card("VARIATEUR I2C")
        self.variator_card.setMinimumHeight(180)

        row_top = QHBoxLayout()
        row_top.setSpacing(6)

        self.lbl_var_state = QLabel("OFFLINE")
        self.lbl_var_state.setObjectName("Value")
        self.lbl_var_state.setStyleSheet("font-size: 14px; font-weight: 700;")
        row_top.addWidget(self.lbl_var_state)

        row_top.addStretch(1)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("MANUAL", 0)
        self.mode_combo.addItem("AUTO", 1)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.mode_combo.setFixedWidth(116)
        self.mode_combo.setFixedHeight(20)
        row_top.addWidget(self.mode_combo)
        var_l.addLayout(row_top)

        self.lbl_var_hint = QLabel("Commande I2C : mode + vitesse cible")
        self.lbl_var_hint.setObjectName("Hint")
        self.lbl_var_hint.setStyleSheet("font-size: 9px;")
        var_l.addWidget(self.lbl_var_hint)

        self.slider_target = QSlider(Qt.Orientation.Horizontal)
        self.slider_target.setRange(0, 60)
        self.slider_target.setValue(0)
        self.slider_target.valueChanged.connect(self._on_slider_changed)
        self.slider_target.setFixedHeight(14)
        var_l.addWidget(self.slider_target)

        row, self.val_var_target = self._kv("Target", "0 km/h")
        var_l.addLayout(row)
        row, self.val_var_speed = self._kv("Measured speed", "0.0 km/h")
        var_l.addLayout(row)
        row, self.val_var_brake = self._kv("Brake", "OFF")
        var_l.addLayout(row)
        row, self.val_var_feedback_mode = self._kv("Reported mode", "MANUAL")
        var_l.addLayout(row)

        left_col.addWidget(self.variator_card, 5)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        self.charger_card, charger_l = self._make_card("CHARGEUR")
        self.charger_card.setMinimumHeight(196)

        self.lbl_charger_state = QLabel("OFFLINE")
        self.lbl_charger_state.setObjectName("Value")
        self.lbl_charger_state.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_charger_state.setStyleSheet("font-size: 15px; font-weight: 700;")
        charger_l.addWidget(self.lbl_charger_state)

        self.lbl_charger_hint = QLabel("Stage: OFF")
        self.lbl_charger_hint.setObjectName("Hint")
        self.lbl_charger_hint.setStyleSheet("font-size: 9px;")
        charger_l.addWidget(self.lbl_charger_hint)

        led_grid = QGridLayout()
        led_grid.setContentsMargins(0, 2, 0, 2)
        led_grid.setHorizontalSpacing(5)
        led_grid.setVerticalSpacing(3)

        self.led_on = LedPill("ON")
        self.led_boost = LedPill("BOOST")
        self.led_equalize = LedPill("EQUALIZE")
        self.led_float = LedPill("FLOAT")
        self.led_failure = LedPill("FAILURE")

        led_grid.addWidget(self.led_on, 0, 0)
        led_grid.addWidget(self.led_boost, 0, 1)
        led_grid.addWidget(self.led_equalize, 1, 0)
        led_grid.addWidget(self.led_float, 1, 1)
        led_grid.addWidget(self.led_failure, 2, 0, 1, 2)
        charger_l.addLayout(led_grid)

        row, self.val_charge_vbat = self._kv("Battery voltage", "--.- V")
        charger_l.addLayout(row)
        row, self.val_charge_ibat = self._kv("Battery current", "--.- A")
        charger_l.addLayout(row)
        row, self.val_charge_p = self._kv("Charge power", "--.- kW")
        charger_l.addLayout(row)
        row, self.val_charge_stage = self._kv("Stage", "--")
        charger_l.addLayout(row)

        right_col.addWidget(self.charger_card, 6)

        self.borne_card, borne_l = self._make_card("BORNE")
        self.borne_card.setMinimumHeight(150)

        self.lbl_borne_state = QLabel("OFFLINE")
        self.lbl_borne_state.setObjectName("Value")
        self.lbl_borne_state.setStyleSheet("font-size: 14px; font-weight: 700;")
        borne_l.addWidget(self.lbl_borne_state)

        self.lbl_borne_hint = QLabel("Préparé pour intégration I2C borne")
        self.lbl_borne_hint.setObjectName("Hint")
        self.lbl_borne_hint.setStyleSheet("font-size: 9px;")
        borne_l.addWidget(self.lbl_borne_hint)

        borne_grid = QGridLayout()
        borne_grid.setContentsMargins(0, 2, 0, 0)
        borne_grid.setHorizontalSpacing(10)
        borne_grid.setVerticalSpacing(2)

        labels = [
            ("Current limit", "0 A"),
            ("Cable limit", "0 A"),
            ("CP duty", "0.0 %"),
            ("CP frequency", "0.0 Hz"),
            ("CP-", "-12.0 V"),
            ("PP", "0.00 V"),
            ("Sector", "ABSENT"),
            ("CP valid", "NO"),
        ]

        self._borne_value_labels = []
        for i, (k_text, v_text) in enumerate(labels):
            key = QLabel(k_text)
            key.setObjectName("Muted")
            key.setStyleSheet("font-size: 9px;")

            val = QLabel(v_text)
            val.setObjectName("Value")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val.setStyleSheet("font-size: 10px;")

            r = i % 4
            c = 0 if i < 4 else 2
            borne_grid.addWidget(key, r, c)
            borne_grid.addWidget(val, r, c + 1)
            self._borne_value_labels.append(val)

        (
            self.val_borne_current,
            self.val_borne_cable,
            self.val_borne_duty,
            self.val_borne_freq,
            self.val_borne_cpneg,
            self.val_borne_pp,
            self.val_borne_sector,
            self.val_borne_cpok,
        ) = self._borne_value_labels

        borne_l.addLayout(borne_grid)
        right_col.addWidget(self.borne_card, 4)

        main_cols.addLayout(left_col, 4)
        main_cols.addLayout(right_col, 6)
        root.addLayout(main_cols)

        hint = QLabel("BMS Health ouvre toutes les données BMS, y compris l’état MOSFET.")
        hint.setObjectName("Hint")
        hint.setStyleSheet("font-size: 9px;")
        root.addWidget(hint)

        root.addStretch(1)

    def _build_overlay(self) -> None:
        self.overlay = QFrame(self)
        self.overlay.hide()
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.overlay.setObjectName("Overlay")

        root = QVBoxLayout(self.overlay)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        header = QFrame(self.overlay)
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setObjectName("Card")
        header.setFixedHeight(38)

        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 6, 12, 6)

        title = QLabel("BMS HEALTH")
        title.setObjectName("CardTitle")
        hl.addWidget(title)

        hl.addStretch(1)

        self.btn_close = QPushButton("CLOSE")
        self.btn_close.setFixedSize(88, 26)
        self.btn_close.clicked.connect(self.hide_overlay)
        hl.addWidget(self.btn_close)

        root.addWidget(header)

        scroll = QScrollArea(self.overlay)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_content = QWidget()
        content = QHBoxLayout(scroll_content)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        summary_card, summary_l = self._make_card("SUMMARY")
        row, self.ov_soc = self._kv("SOC", "-- %")
        summary_l.addLayout(row)
        row, self.ov_vpack = self._kv("Pack voltage", "--.- V")
        summary_l.addLayout(row)
        row, self.ov_current = self._kv("Pack current", "--.- A")
        summary_l.addLayout(row)
        row, self.ov_power = self._kv("Net power", "--.- kW")
        summary_l.addLayout(row)
        row, self.ov_traction_power = self._kv("Traction power", "--.- kW")
        summary_l.addLayout(row)
        row, self.ov_charge_power = self._kv("Charge power", "--.- kW")
        summary_l.addLayout(row)
        row, self.ov_cap = self._kv("Remaining", "--.- Ah")
        summary_l.addLayout(row)
        row, self.ov_cycles = self._kv("Cycles", "--")
        summary_l.addLayout(row)
        left_col.addWidget(summary_card)

        temps_card, temps_l = self._make_card("TEMPERATURES")
        row, self.ov_t1 = self._kv("Sensor 1", "-- °C")
        temps_l.addLayout(row)
        row, self.ov_t2 = self._kv("Sensor 2", "-- °C")
        temps_l.addLayout(row)
        row, self.ov_tmos = self._kv("MOSFET", "-- °C")
        temps_l.addLayout(row)
        left_col.addWidget(temps_card)

        mos_card, mos_l = self._make_card("MOSFETS")
        self.lamp_charge = Lamp("CHARGE")
        self.lamp_discharge = Lamp("DISCHARGE")
        mos_l.addWidget(self.lamp_charge)
        mos_l.addWidget(self.lamp_discharge)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_charge_toggle = QPushButton()
        self.btn_charge_toggle.setFixedHeight(30)
        self.btn_charge_toggle.clicked.connect(self._toggle_charge_mos)
        btn_row.addWidget(self.btn_charge_toggle)

        self.btn_discharge_toggle = QPushButton()
        self.btn_discharge_toggle.setFixedHeight(30)
        self.btn_discharge_toggle.setProperty("variant", "danger")
        self.btn_discharge_toggle.clicked.connect(self._toggle_discharge_mos)
        btn_row.addWidget(self.btn_discharge_toggle)

        mos_l.addLayout(btn_row)
        left_col.addWidget(mos_card)
        left_col.addStretch(1)

        content.addLayout(left_col, 1)

        center_col = QVBoxLayout()
        center_col.setSpacing(8)

        cells_card, cells_l = self._make_card("CELL VOLTAGES")
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.cell_widgets = []
        for i in range(16):
            icon = BatteryIcon(i + 1, cells_card)
            self.cell_widgets.append(icon)
            grid.addWidget(icon, i // 4, i % 4, Qt.AlignmentFlag.AlignCenter)

        cells_l.addLayout(grid)
        center_col.addWidget(cells_card)

        cell_stats_card, cell_stats_l = self._make_card("CELL STATS")
        row, self.ov_vmin = self._kv("Min cell", "--.- V")
        cell_stats_l.addLayout(row)
        row, self.ov_vmax = self._kv("Max cell", "--.- V")
        cell_stats_l.addLayout(row)
        row, self.ov_delta = self._kv("Delta", "--.- V")
        cell_stats_l.addLayout(row)
        center_col.addWidget(cell_stats_card)
        center_col.addStretch(1)

        content.addLayout(center_col, 2)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        diag_card, diag_l = self._make_card("DIAGNOSTICS")
        self.lbl_mask = QLabel("STATUS: 0x0000")
        self.lbl_mask.setObjectName("Value")
        diag_l.addWidget(self.lbl_mask)

        self.al_ov = AlertLamp("OV (Overvoltage)")
        self.al_ot = AlertLamp("OT (Overtemp)")
        self.al_sc = AlertLamp("SC (Short-circuit)")
        diag_l.addWidget(self.al_ov)
        diag_l.addWidget(self.al_ot)
        diag_l.addWidget(self.al_sc)
        right_col.addWidget(diag_card)

        charger_card, charger_l = self._make_card("CHARGER SNAPSHOT")
        row, self.ov_charger_state = self._kv("State", "--")
        charger_l.addLayout(row)
        row, self.ov_charger_source = self._kv("Source", "--")
        charger_l.addLayout(row)
        row, self.ov_charger_stage = self._kv("Stage", "--")
        charger_l.addLayout(row)
        right_col.addWidget(charger_card)

        right_col.addStretch(1)
        content.addLayout(right_col, 1)

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

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
        if self._overlay_host is not None:
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

    def _toggle_charge_mos(self) -> None:
        self.store.request_set_charge_mosfet(not self._charge_on)

    def _toggle_discharge_mos(self) -> None:
        self.store.request_set_discharge_mosfet(not self._discharge_on)

    def _connect_signals(self) -> None:
        self.store.pack_voltage_changed.connect(self._on_vpack)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.cell_min_v.connect(self._on_vmin)
        self.store.cell_max_v.connect(self._on_vmax)
        self.store.cell_delta_v.connect(self._on_delta)
        self.store.cell_voltages_changed.connect(self._on_cells)
        self.store.mosfet_status_changed.connect(self._on_mosfets)
        self.store.bms_status_bitmask.connect(self._on_bitmask)

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
        if hasattr(self.store, "charger_connected_changed"):
            self.store.charger_connected_changed.connect(self._on_charger_connected)
        if hasattr(self.store, "charger_leds_changed"):
            self.store.charger_leds_changed.connect(self._on_charger_leds)

        if self.variator is not None:
            self.variator.telemetry_received.connect(self._on_variator_telemetry)
            self.variator.connection_changed.connect(self._on_variator_connection)

    def _recalc_powers(self) -> None:
        self._power_kw = (self._vpack * self._current) / 1000.0
        self._traction_kw = max(0.0, -self._power_kw)
        self._charge_kw = max(0.0, self._power_kw)

    def _inferred_charger_leds(self) -> tuple[int, int, int, int, int]:
        failure = 1 if (self._bitmask & (self.BIT_OV | self.BIT_OT | self.BIT_SC)) else 0

        if not self._charger_connected and self._charge_kw < 0.05:
            return 0, 0, 0, 0, failure

        on = 1
        boost = 0
        equalize = 0
        float_led = 0

        if self._charge_kw > 0.05:
            if self._soc >= 95:
                float_led = 1
            else:
                boost = 1

        return on, boost, equalize, float_led, failure

    def _charger_stage_text(self, on: int, boost: int, equalize: int, float_led: int, failure: int) -> str:
        if failure:
            return "FAULT"
        if float_led:
            return "FLOAT"
        if equalize:
            return "EQUALIZE"
        if boost:
            return "BOOST"
        if on:
            return "READY"
        return "OFF"

    def _refresh_bms_card(self) -> None:
        self.card_bms.update_data(self._vpack, self._delta, self._vmin, self._vmax)

    def _refresh_mosfet_buttons(self) -> None:
        self.btn_charge_toggle.setText("TURN CHARGE OFF" if self._charge_on else "TURN CHARGE ON")
        self.btn_discharge_toggle.setText("TURN DISCH OFF" if self._discharge_on else "TURN DISCH ON")

    def _refresh_bms_overlay(self) -> None:
        self.ov_soc.setText(f"{self._soc:d} %")
        self.ov_vpack.setText(f"{self._vpack:.1f} V")
        self.ov_current.setText(f"{self._current:.1f} A")
        self.ov_power.setText(f"{self._power_kw:.2f} kW")
        self.ov_traction_power.setText(f"{self._traction_kw:.2f} kW")
        self.ov_charge_power.setText(f"{self._charge_kw:.2f} kW")
        self.ov_cap.setText(f"{self._cap_ah:.1f} Ah")
        self.ov_cycles.setText(f"{self._cycles:d}")

        self.ov_t1.setText(f"{self._t1:.0f} °C")
        self.ov_t2.setText(f"{self._t2:.0f} °C")
        self.ov_tmos.setText(f"{self._tmos:.0f} °C")

        self.ov_vmin.setText(f"{self._vmin:.3f} V")
        self.ov_vmax.setText(f"{self._vmax:.3f} V")
        self.ov_delta.setText(f"{self._delta:.3f} V")

        self.lamp_charge.set_on(self._charge_on)
        self.lamp_discharge.set_on(self._discharge_on)
        self._refresh_mosfet_buttons()

    def _refresh_charger_card(self) -> None:
        if self._charger_leds_seen:
            on = self._charger_led_on
            boost = self._charger_led_boost
            equalize = self._charger_led_equalize
            float_led = self._charger_led_float
            failure = self._charger_led_failure
        else:
            on, boost, equalize, float_led, failure = self._inferred_charger_leds()

        stage = self._charger_stage_text(on, boost, equalize, float_led, failure)

        self.led_on.set_state(on)
        self.led_boost.set_state(boost)
        self.led_equalize.set_state(equalize)
        self.led_float.set_state(float_led)
        self.led_failure.set_state(failure)

        if failure:
            main_state = "FAULT"
        elif self._charge_kw > 0.05:
            main_state = "CHARGING"
        elif self._charger_connected or on:
            main_state = "READY"
        else:
            main_state = "OFFLINE"

        source = "Charger connected" if (self._charger_connected or on) else "No charger detected"

        self.lbl_charger_state.setText(main_state)
        self.lbl_charger_hint.setText(f"Stage: {stage}")

        self.val_charge_vbat.setText(f"{self._vpack:.1f} V")
        self.val_charge_ibat.setText(f"{self._current:.1f} A")
        self.val_charge_p.setText(f"{self._charge_kw:.2f} kW")
        self.val_charge_stage.setText(stage)

        self.ov_charger_state.setText(main_state)
        self.ov_charger_source.setText(source)
        self.ov_charger_stage.setText(stage)

    def _current_mode_value(self) -> int:
        return self._selected_mode

    def _apply_mode_ui_state(self) -> None:
        auto_mode = self._selected_mode == 1
        self.slider_target.setEnabled(auto_mode)
        if auto_mode:
            self.lbl_var_hint.setText(
                "Commande I2C : mode + vitesse cible" if self._variator_connected else "Attente liaison I2C"
            )
        else:
            self.lbl_var_hint.setText(
                "Mode manuel : slider désactivé" if self._variator_connected else "Mode manuel : attente liaison I2C"
            )

    def _send_variator_command(self):
        if self.variator is None:
            return
        self.variator.set_command(self._current_mode_value(), int(self.slider_target.value()))

    def _refresh_variator_card(self) -> None:
        self.lbl_var_state.setText("ONLINE" if self._variator_connected else "OFFLINE")
        self.val_var_target.setText(f"{self.slider_target.value()} km/h")
        self.val_var_speed.setText(f"{self._variator_speed:.1f} km/h")
        self.val_var_brake.setText("ON" if self._variator_brake else "OFF")
        self.val_var_feedback_mode.setText("AUTO" if self._variator_mode == 1 else "MANUAL")
        self._apply_mode_ui_state()

    def _refresh_borne_card(self) -> None:
        self.lbl_borne_state.setText(self._borne_state)
        self.val_borne_current.setText(f"{self._borne_current_limit} A")
        self.val_borne_cable.setText(f"{self._borne_cable_limit} A")
        self.val_borne_duty.setText(f"{self._borne_cp_duty:.1f} %")
        self.val_borne_freq.setText(f"{self._borne_cp_freq:.1f} Hz")
        self.val_borne_cpneg.setText(f"{self._borne_cp_neg:.1f} V")
        self.val_borne_pp.setText(f"{self._borne_pp_voltage:.2f} V")
        self.val_borne_sector.setText("PRESENT" if self._borne_sector_present else "ABSENT")
        self.val_borne_cpok.setText("YES" if self._borne_cp_ok else "NO")

    @Slot(int)
    def _on_slider_changed(self, _value: int):
        self._send_variator_command()
        self._refresh_variator_card()

    @Slot(int)
    def _on_mode_changed(self, index: int):
        self._selected_mode = int(self.mode_combo.itemData(index))
        self._send_variator_command()
        self._refresh_variator_card()

    @Slot(float)
    def _on_vpack(self, v: float):
        self._vpack = float(v)
        self._recalc_powers()
        self._refresh_bms_card()
        self._refresh_bms_overlay()
        self._refresh_charger_card()

    @Slot(float)
    def _on_current(self, a: float):
        self._current = float(a)
        self._recalc_powers()
        self._refresh_bms_overlay()
        self._refresh_charger_card()

    @Slot(float)
    def _on_vmin(self, v: float):
        self._vmin = float(v)
        self._refresh_bms_card()
        self._refresh_bms_overlay()

    @Slot(float)
    def _on_vmax(self, v: float):
        self._vmax = float(v)
        self._refresh_bms_card()
        self._refresh_bms_overlay()

    @Slot(float)
    def _on_delta(self, v: float):
        self._delta = float(v)
        self._refresh_bms_card()
        self._refresh_bms_overlay()

    @Slot(list)
    def _on_cells(self, v_list):
        for i, v in enumerate(v_list):
            if i < len(self.cell_widgets):
                self.cell_widgets[i].set_voltage(v)

    @Slot(bool, bool)
    def _on_mosfets(self, charge_on: bool, discharge_on: bool):
        self._charge_on = bool(charge_on)
        self._discharge_on = bool(discharge_on)
        self._refresh_bms_overlay()

    @Slot(int)
    def _on_bitmask(self, mask: int):
        bm = int(mask) & 0xFFFF
        self._bitmask = bm

        self.lbl_mask.setText(f"STATUS: 0x{bm:04X}")

        self.al_ov.set_alert(bool(bm & self.BIT_OV))
        self.al_ot.set_alert(bool(bm & self.BIT_OT))
        self.al_sc.set_alert(bool(bm & self.BIT_SC))

        self._refresh_charger_card()

    @Slot(int)
    def _on_soc(self, soc: int):
        self._soc = int(soc)
        self._refresh_bms_overlay()
        self._refresh_charger_card()

    @Slot(float)
    def _on_cap(self, ah: float):
        self._cap_ah = float(ah)
        self._refresh_bms_overlay()

    @Slot(int)
    def _on_cycles(self, c: int):
        self._cycles = int(c)
        self._refresh_bms_overlay()

    @Slot(float)
    def _on_t1(self, t: float):
        self._t1 = float(t)
        self._refresh_bms_overlay()

    @Slot(float)
    def _on_t2(self, t: float):
        self._t2 = float(t)
        self._refresh_bms_overlay()

    @Slot(float)
    def _on_tmos(self, t: float):
        self._tmos = float(t)
        self._refresh_bms_overlay()

    @Slot(bool)
    def _on_charger_connected(self, connected: bool):
        self._charger_connected = bool(connected)
        self._refresh_charger_card()

    @Slot(int, int, int, int, int)
    def _on_charger_leds(self, on: int, boost: int, equalize: int, float_led: int, failure: int):
        self._charger_leds_seen = True
        self._charger_led_on = int(on)
        self._charger_led_boost = int(boost)
        self._charger_led_equalize = int(equalize)
        self._charger_led_float = int(float_led)
        self._charger_led_failure = int(failure)
        self._refresh_charger_card()

    @Slot(float, int, bool)
    def _on_variator_telemetry(self, vitesse_kmh: float, mode: int, frein: bool):
        self._variator_speed = float(vitesse_kmh)
        self._variator_mode = int(mode)
        self._variator_brake = bool(frein)
        self._refresh_variator_card()

    @Slot(bool)
    def _on_variator_connection(self, connected: bool):
        self._variator_connected = bool(connected)
        self._refresh_variator_card()