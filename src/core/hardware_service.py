from __future__ import annotations
import serial
import time
from .base_data_service import BaseDataService

PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
BAUD = 115200

class HardwareService(BaseDataService):
    def run(self) -> None:
        self._running = True
        print(f"🚀 [BMS] Démarrage sur {PORT} (Mode JK-NW)")
        
        try:
            with serial.Serial(PORT, BAUD, timeout=1.0) as ser:
                while self._running:
                    # 1. Préparation de la requête (Exactement comme ton script)
                    req = self._build_jk_request()
                    ser.reset_input_buffer()
                    ser.write(req)
                    ser.flush()
                    
                    # 2. Lecture avec synchronisation (cherche 4E 57)
                    time.sleep(0.12)
                    frame = self._read_jk_frame(ser)
                    
                    if frame:
                        self._decode_jk_data(frame)
                    else:
                        # On ne print que si on veut débugger, sinon ça pollue
                        pass
                    
                    time.sleep(0.5) 
                    
        except Exception as e:
            print(f"❌ [BMS] Erreur Port : {e}")

    def _build_jk_request(self) -> bytes:
        STX = b"\x4E\x57"
        # Terminal(4) + Cmd(0x06) + Src(0x03) + Type(0x00) + Data_ID(0x00) + Record(4) + ETX(0x68)
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        # Formule JK : Longueur = 2 (soi-même) + corps + 4 (checksum)
        length_val = 2 + len(body) + 4 
        ln_bytes = length_val.to_bytes(2, "big")
        
        frame_wo_chk = STX + ln_bytes + body
        chk = sum(frame_wo_chk) & 0xFFFF
        # Checksum sur 4 octets (00 00 XX YY)
        return frame_wo_chk + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> bytes | None:
        start_time = time.time()
        buf = bytearray()
        # On synchronise pour trouver 'NW'
        while time.time() - start_time < 2.0:
            b = ser.read(1)
            if not b: continue
            buf += b
            if len(buf) >= 2 and buf[-2:] == b"\x4E\x57":
                break
        else: return None

        # Lire la longueur
        ln_data = ser.read(2)
        if len(ln_data) < 2: return None
        length = int.from_bytes(ln_data, "big")
        
        # Lire le reste (la longueur inclut le champ longueur, donc on lit length - 2)
        rest = ser.read(length - 2)
        return bytes(b"\x4E\x57" + ln_data + rest)

    def _decode_jk_data(self, frame: bytes):
        # Payload : saute STX(2), LEN(2), TERM(4), CMD(1), SRC(1), TYPE(1) -> Index 11
        # Retire ETX(1) et CHK(4) -> -5
        payload = frame[11:-5]
        
        def get_val(code: int, size: int):
            idx = payload.find(bytes([code]))
            if idx == -1 or idx + 1 + size > len(payload): return None
            return int.from_bytes(payload[idx+1:idx+1+size], "big")

        # ⚡ Tension (0x83)
        v_raw = get_val(0x83, 2)
        if v_raw:
            voltage = v_raw * 0.01
            print(f"⚡ BMS -> {voltage:.2f}V")
            self.state_store.pack_voltage_changed.emit(voltage)

        # 🔋 SOC (0x85)
        soc = get_val(0x85, 1)
        if soc:
            print(f"🔋 BMS -> {soc}%")
            self.state_store.soc_changed.emit(soc)

        # 🔌 Courant (0x84)
        c_raw = get_val(0x84, 2)
        if c_raw:
            val = (c_raw & 0x7FFF) * 0.01
            current = val if c_raw & 0x8000 else -val
            self.state_store.pack_current_changed.emit(current)