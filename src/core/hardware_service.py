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
    - Décode 0x89 (capacité restante)
    - Utilise UNIQUEMENT les setters du StateStore
    """

    # Bits MOSFET (placeholder -> ajuste selon ta table JK si besoin)
    CHARGE_MOSFET_MASK = 0x0001
    DISCHARGE_MOSFET_MASK = 0x0002

    def __init__(self, state_store, port: str, baud: int = DEFAULT_BAUD, parent=None) -> None:
        super().__init__(state_store, parent=parent)
        self.port = port
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
                        # Silence total: pas de print.
                        continue

        except Exception:
            # Silence total: pas de print.
            return

    def _build_jk_request(self) -> bytes:
        stx = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length_val = 2 + len(body) + 4  # len-field + body + chk + tail
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
        if length < 2:
            return None

        rest = ser.read(length - 2)
        if len(rest) < (length - 2):
            return None

        return bytes(b"\x4E\x57" + ln_data + rest)

    def _decode_all_jk_data(self, frame: bytes) -> None:
        # Format selon ton implémentation existante: data=frame[11:-5]
        data = frame[11:-5]
        offset = 0

        cell_voltages: list[float] = []

        while offset < len(data):
            marker = data[offset]

            # 0x79: cellules (block)
            if marker == 0x79:
                if offset + 2 >= len(data):
                    break
                block_len = data[offset + 1]
                end = offset + 2 + block_len
                if end > len(data):
                    break

                cell_bytes = data[offset + 2 : end]
                # pattern: [cell_id][V_hi][V_lo] * N
                for i in range(0, len(cell_bytes), 3):
                    if i + 2 >= len(cell_bytes):
                        break
                    v = ((cell_bytes[i + 1] << 8) | cell_bytes[i + 2]) / 1000.0
                    cell_voltages.append(v)

                offset = end
                continue

            # 0x83: pack voltage (0.01 V)
            if marker == 0x83:
                if offset + 3 > len(data):
                    break
                v_pack = int.from_bytes(data[offset + 1 : offset + 3], "big") * 0.01
                self.state_store.set_pack_voltage(v_pack)
                offset += 3
                continue

            # 0x84: current (0.01 A signed)
            if marker == 0x84:
                if offset + 3 > len(data):
                    break
                c_raw = int.from_bytes(data[offset + 1 : offset + 3], "big")
                amps = (c_raw & 0x7FFF) * 0.01
                if not (c_raw & 0x8000):
                    amps = -amps
                self.state_store.set_pack_current(amps)
                offset += 3
                continue

            # 0x85: SOC %
            if marker == 0x85:
                if offset + 2 > len(data):
                    break
                self.state_store.set_soc(int(data[offset + 1]))
                offset += 2
                continue

            # 0x81: temp sensor 1 (batt)
            if marker == 0x81:
                if offset + 3 > len(data):
                    break
                t = self._parse_temp(int.from_bytes(data[offset + 1 : offset + 3], "big"))
                self.state_store.set_batt_temp(t)
                offset += 3
                continue

            # 0x87: cycle count
            if marker == 0x87:
                if offset + 3 > len(data):
                    break
                cycles = int.from_bytes(data[offset + 1 : offset + 3], "big")
                self.state_store.set_cycle_count(cycles)
                offset += 3
                continue

            # 0x89: remaining capacity (Ah) => *0.001
            if marker == 0x89:
                if offset + 5 > len(data):
                    break
                cap = int.from_bytes(data[offset + 1 : offset + 5], "big") * 0.001
                self.state_store.set_capacity_remaining_ah(cap)
                offset += 5
                continue

            # 0x8B: status bitmask (16-bit) + MOSFET derivation
            if marker == 0x8B:
                if offset + 3 > len(data):
                    break
                status = int.from_bytes(data[offset + 1 : offset + 3], "big") & 0xFFFF
                self.state_store.set_bms_status_bitmask(status)

                charge_on = bool(status & self.CHARGE_MOSFET_MASK)
                discharge_on = bool(status & self.DISCHARGE_MOSFET_MASK)
                self.state_store.set_mosfet_status(charge_on, discharge_on)

                offset += 3
                continue

            # alarms 0x90..0x96 (skip 2 bytes)
            if 0x90 <= marker <= 0x96:
                if offset + 2 > len(data):
                    break
                offset += 2
                continue

            offset += 1

        if cell_voltages:
            self.state_store.set_cell_voltages(cell_voltages)

    @staticmethod
    def _parse_temp(val: int) -> float:
        # Conservé (logique existante): >100 => négatif
        if val > 100:
            return float(-(val - 100))
        return float(val)
