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
        print(f"🚀 [BMS] Démarrage du service sur {PORT}...")
        
        try:
            with serial.Serial(PORT, BAUD, timeout=0.5) as ser:
                print(f"✅ [BMS] Port série ouvert. Attente des données...")
                
                while self._running:
                    # 1. Envoi requête Read All (NW...)
                    req = self._build_jk_request()
                    ser.reset_input_buffer() # On vide le tampon pour être propre
                    ser.write(req)
                    
                    # 2. Lecture de la trame
                    time.sleep(0.15) # Pause pour laisser le BMS répondre
                    frame = self._read_jk_frame(ser)
                    
                    if frame:
                        # print(f"📥 [BMS] Trame reçue ({len(frame)} octets)")
                        self._decode_jk_data(frame)
                    else:
                        print("⚠️ [BMS] Aucune réponse (Timeout ou câble débranché)")
                    
                    time.sleep(0.4) # Fréquence ~2Hz
                    
        except Exception as e:
            print(f"❌ [BMS] Erreur fatale : {e}")
        finally:
            print("🛑 [BMS] Service arrêté.")

    def _build_jk_request(self) -> bytes:
        # Construction trame standard JK NW pour Read All Data (0x06)
        header = b"\x4E\x57"
        # terminal(4) + cmd(0x06) + src(0x03) + type(0x00) + data_id(0x00) + record(4) + end(0x68)
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length = (len(body) + 4).to_bytes(2, "big")
        frame = header + length + body
        chk = sum(frame) & 0xFFFF
        return frame + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> bytes | None:
        # On cherche le marqueur de début NW
        start = ser.read(2)
        if start != b"\x4E\x57":
            return None
            
        # On lit la longueur (2 octets)
        length_bytes = ser.read(2)
        if len(length_bytes) < 2:
            return None
            
        length = int.from_bytes(length_bytes, "big")
        # On lit le reste de la trame (data + checksum)
        payload = ser.read(length)
        return start + length_bytes + payload

    def _decode_jk_data(self, frame: bytes):
        # Le payload utile commence après l'en-tête (STX, LEN, etc.)
        payload = frame[11:-5]
        
        # Helper interne pour extraire une valeur par son ID
        def get_val(code: int, size: int):
            idx = payload.find(bytes([code]))
            if idx == -1 or (idx + 1 + size) > len(payload):
                return None
            return int.from_bytes(payload[idx+1:idx+1+size], "big")

        # --- Extraction & Émission ---
        v_raw = get_val(0x83, 2)
        if v_raw is not None:
            voltage = v_raw * 0.01
            print(f"⚡ [BMS] Tension Pack : {voltage:.2f}V")
            self.state_store.pack_voltage_changed.emit(voltage)

        soc = get_val(0x85, 1)
        if soc is not None:
            print(f"🔋 [BMS] SOC : {soc}%")
            self.state_store.soc_changed.emit(soc)

        c_raw = get_val(0x84, 2)
        if c_raw is not None:
            # Décodage courant (bit 15 = signe)
            val = (c_raw & 0x7FFF) * 0.01
            current = val if c_raw & 0x8000 else -val
            print(f"🔌 [BMS] Courant : {current:.2f}A")
            self.state_store.pack_current_changed.emit(round(current, 2))