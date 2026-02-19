from __future__ import annotations

import time
from typing import Optional

import serial

from .base_data_service import BaseDataService

DEFAULT_BMS_PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
DEFAULT_BAUD = 115200


class HardwareService(BaseDataService):
    def __init__(
        self,
        state_store,
        port: str,
        baud: int = DEFAULT_BAUD,
        parent=None,
    ) -> None:
        super().__init__(state_store, parent=parent)
        self.port = port
        self.baud = int(baud)

    def run(self) -> None:
        self._running = True

        if not self.port:
            print("❌ [BMS] Port série vide. Lance avec: python main.py --port /dev/ttyUSB0")
            return

        print(f"✅ [BMS] Démarrage Scan Intégral sur {self.port} @ {self.baud}")

        try:
            with serial.Serial(self.port, self.baud, timeout=1.0) as ser:
                while self._running:
                    req = self._build_jk_request()

                    ser.reset_input_buffer()
                    ser.write(req)
                    ser.flush()

                    time.sleep(0.15)

                    frame = self._read_jk_frame(ser)
                    if frame:
                        self._decode_all_jk_data(frame)

                    time.sleep(0.4)

        except Exception as e:
            print(f"❌ [BMS] Erreur : {e}")

    def _build_jk_request(self) -> bytes:
        stx = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"

        length_val = 2 + len(body) + 4  # (len field + body + chk + end bytes)
        frame_wo_chk = stx + length_val.to_bytes(2, "big") + body

        chk = sum(frame_wo_chk) & 0xFFFF
        return frame_wo_chk + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> Optional[bytes]:
        start_time = time.time()
        buf = bytearray()

        while time.time() - start_time < 1.5:
            b = ser.read(1)
            if not b:
                continue

            buf += b
            if len(buf) >= 2 and buf[-2:] == b"\x4E\x57":
                break
        else:
            return None

        ln_data = ser.read(2)
        if len(ln_data) < 2:
            return None

        length = int.from_bytes(ln_data, "big")
        rest = ser.read(length - 2)
        if len(rest) < (length - 2):
            return None

        return bytes(b"\x4E\x57" + ln_data + rest)

    def _decode_all_jk_data(self, frame: bytes) -> None:
        # Données JK : frame[11:-5] d'après ton implémentation actuelle
        data = frame[11:-5]
        offset = 0

        voltages: list[float] = []

        while offset < len(data):
            marker = data[offset]

            # --- BLOC CELLULES (0x79) ---
            if marker == 0x79:
                if offset + 2 >= len(data):
                    break
                block_len = data[offset + 1]
                end = offset + 2 + block_len
                if end > len(data):
                    break

                cell_bytes = data[offset + 2 : end]

                # Format observé : [cell_id][V_hi][V_lo] répété
                for i in range(0, len(cell_bytes), 3):
                    if i + 2 >= len(cell_bytes):
                        break
                    v = ((cell_bytes[i + 1] << 8) | cell_bytes[i + 2]) / 1000.0
                    voltages.append(v)

                offset = end
                continue

            # --- TOTAL VOLTAGE (0x83) ---
            if marker == 0x83:
                if offset + 3 > len(data):
                    break
                v_pack = int.from_bytes(data[offset + 1 : offset + 3], "big") * 0.01
                self.state_store.set_pack_voltage(v_pack)
                offset += 3
                continue

            # --- CURRENT (0x84) ---
            if marker == 0x84:
                if offset + 3 > len(data):
                    break
                c_raw = int.from_bytes(data[offset + 1 : offset + 3], "big")
                current = (c_raw & 0x7FFF) * 0.01
                if not (c_raw & 0x8000):
                    current = -current
                self.state_store.set_pack_current(current)
                offset += 3
                continue

            # --- SOC (0x85) ---
            if marker == 0x85:
                if offset + 2 > len(data):
                    break
                self.state_store.set_soc(int(data[offset + 1]))
                offset += 2
                continue

            # --- TEMP MOSFET (0x80) ---
            if marker == 0x80:
                if offset + 3 > len(data):
                    break
                t = self._parse_temp(int.from_bytes(data[offset + 1 : offset + 3], "big"))
                self.state_store.set_temp_mosfet(t)
                offset += 3
                continue

            # --- TEMP SENSOR 1 (0x81) => Batterie ---
            if marker == 0x81:
                if offset + 3 > len(data):
                    break
                t = self._parse_temp(int.from_bytes(data[offset + 1 : offset + 3], "big"))
                self.state_store.set_temp_sensor_1(t)
                self.state_store.set_batt_temp(t)
                offset += 3
                continue

            # --- TEMP SENSOR 2 (0x82) ---
            if marker == 0x82:
                if offset + 3 > len(data):
                    break
                t = self._parse_temp(int.from_bytes(data[offset + 1 : offset + 3], "big"))
                self.state_store.set_temp_sensor_2(t)
                offset += 3
                continue

            # --- CYCLE COUNT (0x87) ---
            if marker == 0x87:
                if offset + 3 > len(data):
                    break
                cycles = int.from_bytes(data[offset + 1 : offset + 3], "big")
                self.state_store.set_cycle_count(cycles)
                offset += 3
                continue

            # --- CAPACITÉ RESTANTE (0x89) ---
            if marker == 0x89:
                if offset + 5 > len(data):
                    break
                cap = int.from_bytes(data[offset + 1 : offset + 5], "big") * 0.001
                self.state_store.set_capacity_remaining_ah(cap)
                offset += 5
                continue

            # --- STATUS (0x8B) ---
            if marker == 0x8B:
                if offset + 3 > len(data):
                    break
                status = int.from_bytes(data[offset + 1 : offset + 3], "big")
                self.state_store.set_bms_status_bitmask(status)
                offset += 3
                continue

            # --- ALARMS (0x90..0x96) ---
            if 0x90 <= marker <= 0x96:
                # Placeholder (tu pourras raffiner plus tard)
                # offset+1 = valeur / flags etc. selon protocole
                if offset + 2 > len(data):
                    break
                offset += 2
                continue

            # Inconnu => avance d’1
            offset += 1

        # Après scan, push data cellules (source de vérité)
        if voltages:
            self.state_store.set_cell_data(voltages)
            v_min, v_max = min(voltages), max(voltages)
            print(
                f"✅ [BMS] {len(voltages)} cells | "
                f"V_max: {v_max:.3f}V | V_min: {v_min:.3f}V | Δ: {(v_max - v_min):.3f}V"
            )

    def _parse_temp(self, val: int) -> float:
        """
        Décodage température JK BMS (d'après ta logique actuelle).
        """
        if val > 100:
            return float(-(val - 100))
        return float(val)
