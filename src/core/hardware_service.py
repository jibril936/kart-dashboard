from __future__ import annotations

import time
from typing import Optional, Tuple
from collections import deque
from threading import Lock

import serial
from PyQt6.QtCore import pyqtSlot

from .base_data_service import BaseDataService

DEFAULT_BMS_PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
DEFAULT_BAUD = 115200


class HardwareService(BaseDataService):
    """
    JK BMS via RS485 (USB-Série)

    - Lecture: protocole 4E57 (read-all)
    - Ecriture MOSFET: "Written instructions" (cmd 0x02) + ID 0xAB/0xAC (1 byte)
    - SILENCE TOTAL: pas de print() (la UI est la source de feedback)
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
        0x8E: 2,
        0x8F: 2,
    }

    # MOS control IDs (JK RS485 protocol)
    MOS_CHARGE_ID = 0xAB
    MOS_DISCHARGE_ID = 0xAC

    def __init__(self, state_store, port: str, baud: int = DEFAULT_BAUD, parent=None) -> None:
        super().__init__(state_store, parent=parent)
        self.port = port or DEFAULT_BMS_PORT
        self.baud = int(baud)

        self._cmd_lock = Lock()
        self._pending_cmds: deque[Tuple[int, int]] = deque(maxlen=16)  # (identifier, value)

    # -------------------------
    # Public slots (called from main thread via signals)
    # -------------------------
    @pyqtSlot(bool)
    def request_set_charge_mosfet(self, enable: bool) -> None:
        self._enqueue_cmd(self.MOS_CHARGE_ID, 1 if enable else 0)

    @pyqtSlot(bool)
    def request_set_discharge_mosfet(self, enable: bool) -> None:
        self._enqueue_cmd(self.MOS_DISCHARGE_ID, 1 if enable else 0)

    def _enqueue_cmd(self, identifier: int, value: int) -> None:
        with self._cmd_lock:
            self._pending_cmds.append((int(identifier) & 0xFF, int(value) & 0xFF))

    def _pop_cmd(self) -> Optional[Tuple[int, int]]:
        with self._cmd_lock:
            if not self._pending_cmds:
                return None
            return self._pending_cmds.popleft()

    # -------------------------
    # Thread loop
    # -------------------------
    def run(self) -> None:
        self._running = True
        try:
            with serial.Serial(self.port, self.baud, timeout=1.0, write_timeout=1.0) as ser:
                while self._running:
                    try:
                        # 1) Apply pending write commands (at most 2 per loop)
                        for _ in range(2):
                            cmd = self._pop_cmd()
                            if cmd is None:
                                break
                            ident, val = cmd
                            self._send_write_cmd(ser, ident, val)
                            time.sleep(0.08)

                        # 2) Read-all polling
                        req = self._build_jk_request()
                        ser.reset_input_buffer()
                        ser.write(req)
                        ser.flush()

                        time.sleep(0.15)

                        frame = self._read_jk_frame(ser)
                        if frame:
                            self._decode_all_jk_data(frame)

                        time.sleep(0.35)
                    except Exception:
                        continue
        except Exception:
            return

    # -------------------------
    # Frame IO
    # -------------------------
    def _build_jk_request(self) -> bytes:
        # 4E 57 + LEN + payload + 00 00 + checksum(2)
        stx = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length_val = 2 + len(body) + 4
        frame_wo_chk = stx + length_val.to_bytes(2, "big") + body
        chk = sum(frame_wo_chk) & 0xFFFF
        return frame_wo_chk + b"\x00\x00" + chk.to_bytes(2, "big")

    def _send_write_cmd(self, ser: serial.Serial, identifier: int, value: int) -> None:
        # cmd 0x02 (written instructions)
        stx = b"\x4E\x57"
        terminal_id = b"\x00\x00\x00\x00"
        cmd = b"\x02"
        src = b"\x03"
        transport = b"\x00"
        info = bytes([identifier & 0xFF, value & 0xFF])
        record = b"\x00\x00\x00\x00"
        end = b"\x68"

        body = terminal_id + cmd + src + transport + info + record + end
        length_val = 2 + len(body) + 4
        frame_wo = stx + length_val.to_bytes(2, "big") + body
        chk = sum(frame_wo) & 0xFFFF
        frame = frame_wo + b"\x00\x00" + chk.to_bytes(2, "big")

        ser.write(frame)
        ser.flush()

        # optional ACK read (silencieux)
        try:
            _ = self._read_jk_frame(ser)
        except Exception:
            pass

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

    # -------------------------
    # Decode
    # -------------------------
    def _decode_all_jk_data(self, frame: bytes) -> None:
        # IMPORTANT: end of frame includes record(4) + end(1) + checksum(4) -> 9 bytes
        data = frame[11:-9]
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

            ln = self.TAG_LEN.get(marker)
            if ln is None:
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
        if marker == 0x80:
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_mosfet"):
                self.state_store.set_temp_mosfet(t)
            return

        if marker == 0x81:
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_sensor_1"):
                self.state_store.set_temp_sensor_1(t)
            return

        if marker == 0x82:
            t = self._parse_temp(int.from_bytes(payload, "big"))
            if hasattr(self.state_store, "set_temp_sensor_2"):
                self.state_store.set_temp_sensor_2(t)
            if hasattr(self.state_store, "set_batt_temp"):
                self.state_store.set_batt_temp(t)
            return

        if marker == 0x83:
            v_pack = int.from_bytes(payload, "big") * 0.01
            self.state_store.set_pack_voltage(v_pack)
            return

        if marker == 0x84:
            raw = int.from_bytes(payload, "big") & 0xFFFF
            amps = self._decode_current(raw)
            self.state_store.set_pack_current(amps)
            return

        if marker == 0x85:
            self.state_store.set_soc(int(payload[0]))
            return

        if marker == 0x87:
            cycles = int.from_bytes(payload, "big")
            self.state_store.set_cycle_count(cycles)
            return

        if marker == 0x89:
            cap = int.from_bytes(payload, "big") * 0.001
            self.state_store.set_capacity_remaining_ah(cap)
            return

        if marker == 0x8B:
            warn = int.from_bytes(payload, "big") & 0xFFFF
            self.state_store.set_bms_status_bitmask(warn)
            return

        if marker == 0x8C:
            status = int.from_bytes(payload, "big") & 0xFFFF
            charge_on = bool(status & 0x0001)
            discharge_on = bool(status & 0x0002)
            self.state_store.set_mosfet_status(charge_on, discharge_on)
            return

    @staticmethod
    def _parse_temp(val: int) -> float:
        if val > 100:
            return float(-(val - 100))
        return float(val)

    @staticmethod
    def _decode_current(raw: int) -> float:
        if raw & 0x8000:
            return (raw & 0x7FFF) * 0.01
        if 8000 <= raw <= 12000:
            return (10000 - raw) * 0.01
        if raw == 0:
            return 0.0
        return -(raw * 0.01)
