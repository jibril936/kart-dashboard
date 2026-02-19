from __future__ import annotations

import time
from typing import Optional

import serial

from .base_data_service import BaseDataService

DEFAULT_BMS_PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
DEFAULT_BAUD = 115200


class HardwareService(BaseDataService):
    """
    BMS JK via RS485 (USB-Série)

    - SILENCE TOTAL: aucun print()
    - Utilise UNIQUEMENT les setters du StateStore
    - Protocole JK LCD (4E 57 ...), tags TLV:
        0x79 cellules (len + 3*n)
        0x80 temp MOS/power tube (2)
        0x81 temp battery box (2)
        0x82 temp battery (2)
        0x83 Vpack (2) *0.01
        0x84 courant (2) -> encodage variable selon firmware
        0x85 SOC (1)
        0x87 cycle count (2)
        0x89 capacité restante/cycle capacity (4) *0.001 (Ah) [selon ton besoin]
        0x8B warning bitmask (2)
        0x8C status info bitmask (2) => MOSFET charge/discharge
    """

    # Longueurs fixes (hors 0x79 qui a son byte len)
    TAG_LEN = {
        0x80: 2,
        0x81: 2,
        0x82: 2,
        0x83: 2,
        0x84: 2,
        0x85: 1,
        0x86: 1,
        0x87: 2,
        0x89: 4,
        0x8A: 2,
        0x8B: 2,
        0x8C: 2,
        # on ignore le reste proprement sans casser l'alignement quand c'est possible
        0x8E: 2,
        0x8F: 2,
    }

    def __init__(self, state_store, port: str, baud: int = DEFAULT_BAUD, parent=None) -> None:
        super().__init__(state_store, parent=parent)
        self.port = port or DEFAULT_BMS_PORT
        self.baud = int(baud)

    def run(self) -> None:
        self._running = True
        try:
            with serial.Serial(self.port, self.baud, timeout=1.0) as ser:
                while self._running:
                    try:
                        req = self._build_jk_request()
                        ser.reset_input_buffer()
                        ser.write(req)
                        ser.flush()

                        time.sleep(0.15)

                        frame = self._read_jk_frame(ser)
                        if frame:
                            self._decode_all_jk_data(frame)

                        time.sleep(0.4)
                    except Exception:
                        # Silence total
                        continue
        except Exception:
            # Silence total
            return

    def _build_jk_request(self) -> bytes:
        # Exemple protocole:
        # 4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68 00 00 CHK_HI CHK_LO
        stx = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length_val = 2 + len(body) + 4  # len-field + body + (00 00) + chk(2)
        frame_wo_chk = stx + length_val.to_bytes(2, "big") + body
        chk = sum(frame_wo_chk) & 0xFFFF
        return frame_wo_chk + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> Optional[bytes]:
        start_time = time.time()
        buf = bytearray()

        # sync on 4E 57
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
        if length < 2:
            return None

        rest = ser.read(length - 2)
        if len(rest) < (length - 2):
            return None

        return bytes(b"\x4E\x57" + ln_data + rest)

    def _decode_all_jk_data(self, frame: bytes) -> None:
        # Dans l'exemple JK LCD, le 1er tag commence à l'index 11
        data = frame[11:-5]
        offset = 0

        cell_voltages: list[float] = []

        while offset < len(data):
            marker = data[offset]

            # 0x79: cellules (block len + payload)
            if marker == 0x79:
                if offset + 2 > len(data):
                    break
                block_len = data[offset + 1]
                end = offset + 2 + block_len
                if end > len(data):
                    break

                cell_bytes = data[offset + 2:end]
                for i in range(0, len(cell_bytes), 3):
                    if i + 2 >= len(cell_bytes):
                        break
                    v = ((cell_bytes[i + 1] << 8) | cell_bytes[i + 2]) / 1000.0
                    cell_voltages.append(v)

                offset = end
                continue

            # tags à longueur fixe
            ln = self.TAG_LEN.get(marker)
            if ln is None:
                # Pour éviter de partir en vrille sur les tags "string" (B4..BA..),
                # on s'arrête dès qu'on entre dans les zones non gérées.
                # (Nos données utiles sont toutes < 0x8D.)
                if marker >= 0x8D:
                    break
                offset += 1
                continue

            if offset + 1 + ln > len(data):
                break

            payload = data[offset + 1: offset + 1 + ln]
            self._handle_tag(marker, payload)
            offset += 1 + ln

        if cell_voltages:
            self.state_store.set_cell_voltages(cell_voltages)

    def _handle_tag(self, marker: int, payload: bytes) -> None:
        # Temps
        if marker == 0x80:  # power tube (MOSFET)
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_mosfet"):
                self.state_store.set_temp_mosfet(t)
            return

        if marker == 0x81:  # battery box
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_sensor_1"):
                self.state_store.set_temp_sensor_1(t)
            return

        if marker == 0x82:  # battery temp
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_sensor_2"):
                self.state_store.set_temp_sensor_2(t)
            # compat / UI existante
            if hasattr(self.state_store, "set_batt_temp"):
                self.state_store.set_batt_temp(t)
            return

        # Vpack
        if marker == 0x83:
            v_pack = int.from_bytes(payload, "big") * 0.01
            self.state_store.set_pack_voltage(v_pack)
            return

        # Courant (robuste: 2 encodages possibles)
        if marker == 0x84:
            raw = int.from_bytes(payload, "big") & 0xFFFF
            amps = self._decode_current(raw)
            self.state_store.set_pack_current(amps)
            return

        # SOC
        if marker == 0x85:
            self.state_store.set_soc(int(payload[0]))
            return

        # Cycles
        if marker == 0x87:
            cycles = int.from_bytes(payload, "big")
            self.state_store.set_cycle_count(cycles)
            return

        # Capacité restante (Ah)
        if marker == 0x89:
            cap = int.from_bytes(payload, "big") * 0.001
            self.state_store.set_capacity_remaining_ah(cap)
            return

        # Warning bitmask
        if marker == 0x8B:
            warn = int.from_bytes(payload, "big") & 0xFFFF
            self.state_store.set_bms_status_bitmask(warn)
            return

        # Status info => MOSFET states
        if marker == 0x8C:
            status = int.from_bytes(payload, "big") & 0xFFFF
            charge_on = bool(status & 0x0001)
            discharge_on = bool(status & 0x0002)
            self.state_store.set_mosfet_status(charge_on, discharge_on)
            return

    @staticmethod
    def _parse_temp(val: int) -> float:
        # 0-140 (-40..100), >100 => négatif (100 référence)
        if val > 100:
            return float(-(val - 100))
        return float(val)

    @staticmethod
    def _decode_current(raw: int) -> float:
        """
        Deux encodages rencontrés:
        A) "redefined current" : bit15 = 1 charge, 0 décharge ; magnitude en 0.01A
           - décharge 20A => 0x07D0 (2000)
           - charge 20A   => 0x87D0 (bit15 + 2000)
        B) "offset 10000" : 10000 = 0A
           - décharge -10A => 11000
           - charge  +5A   => 9500
        """
        # Mode A charge: bit 15 set
        if raw & 0x8000:
            return (raw & 0x7FFF) * 0.01

        # Heuristique mode B (autour de 10000)
        if 8000 <= raw <= 12000:
            return (10000 - raw) * 0.01

        # Mode A décharge: magnitude directe, signe négatif
        if raw == 0:
            return 0.0
        return -(raw * 0.01)
