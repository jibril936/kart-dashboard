from __future__ import annotations
import serial
import time
from .base_data_service import BaseDataService

# Config du port (celle de ton test réussi)
PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
BAUD = 115200

class HardwareService(BaseDataService):
    def run(self) -> None:
        self._running = True
        try:
            with serial.Serial(PORT, BAUD, timeout=0.5) as ser:
                while self._running:
                    # 1. Envoi requête Read All (NW...)
                    req = self._build_jk_request()
                    ser.write(req)
                    
                    # 2. Lecture de la trame
                    time.sleep(0.12)
                    frame = self._read_jk_frame(ser)
                    
                    if frame:
                        self._decode_jk_data(frame)
                    
                    time.sleep(0.4) # Fréquence de lecture (2.5 Hz)
        except Exception as e:
            print(f"BMS Error: {e}")

    def _build_jk_request(self) -> bytes:
        # Construction trame standard JK NW pour Read All Data
        header = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length = (len(body) + 4).to_bytes(2, "big")
        frame = header + length + body
        chk = sum(frame) & 0xFFFF
        return frame + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> bytes | None:
        # Sync sur NW
        if ser.read(2) != b"\x4E\x57": return None
        length = int.from_bytes(ser.read(2), "big")
        return b"\x4E\x57" + length.to_bytes(2, "big") + ser.read(length)

    def _decode_jk_data(self, frame: bytes):
        payload = frame[11:-5]
        
        # Helper pour trouver une valeur par son ID
        def get_val(code: int, size: int):
            idx = payload.find(bytes([code]))
            if idx == -1: return None
            return int.from_bytes(payload[idx+1:idx+1+size], "big")

        # Extraction & Emission vers le StateStore
        v_raw = get_val(0x83, 2)
        if v_raw: self.state_store.pack_voltage_changed.emit(v_raw * 0.01)

        soc = get_val(0x85, 1)
        if soc: self.state_store.soc_changed.emit(soc)

        c_raw = get_val(0x84, 2)
        if c_raw:
            # Décodage courant (bit 15 = signe)
            val = (c_raw & 0x7FFF) * 0.01
            current = val if c_raw & 0x8000 else -val
            self.state_store.pack_current_changed.emit(round(current, 2))