from __future__ import annotations
import serial
import time
from .base_data_service import BaseDataService

PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10OGOT8-if00-port0"
BAUD = 115200

class HardwareService(BaseDataService):
    def run(self) -> None:
        self._running = True
        print(f"🚀 [BMS] Démarrage Scan Intégral sur {PORT}")
        
        try:
            with serial.Serial(PORT, BAUD, timeout=1.0) as ser:
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
        STX = b"\x4E\x57"
        body = b"\x00\x00\x00\x00\x06\x03\x00\x00\x00\x00\x00\x00\x68"
        length_val = 2 + len(body) + 4 
        frame_wo_chk = STX + length_val.to_bytes(2, "big") + body
        chk = sum(frame_wo_chk) & 0xFFFF
        return frame_wo_chk + b"\x00\x00" + chk.to_bytes(2, "big")

    def _read_jk_frame(self, ser) -> bytes | None:
        start_time = time.time()
        buf = bytearray()
        while time.time() - start_time < 1.5:
            b = ser.read(1)
            if not b: continue
            buf += b
            if len(buf) >= 2 and buf[-2:] == b"\x4E\x57":
                break
        else: return None

        ln_data = ser.read(2)
        if len(ln_data) < 2: return None
        length = int.from_bytes(ln_data, "big")
        rest = ser.read(length - 2)
        return bytes(b"\x4E\x57" + ln_data + rest)

    def _decode_all_jk_data(self, frame: bytes):
        # On saute l'en-tête pour arriver au début des données (index 11)
        # On s'arrête avant le marqueur de fin 0x68 et le checksum (index -5)
        data = frame[11:-5]
        offset = 0
        
        # Variables temporaires pour calculs groupés
        voltages = []
        
        while offset < len(data):
            marker = data[offset]
            
            # --- BLOC CELLULES (0x79) ---
            if marker == 0x79:
                block_len = data[offset+1]
                cell_bytes = data[offset+2 : offset+2+block_len]
                for i in range(0, len(cell_bytes), 3):
                    v = ((cell_bytes[i+1] << 8) | cell_bytes[i+2]) / 1000.0
                    voltages.append(v)
                offset += 2 + block_len

            # --- TENSIONS / COURANT / SOC ---
            elif marker == 0x83: # Total Voltage
                v_pack = int.from_bytes(data[offset+1:offset+3], "big") * 0.01
                self.state_store.pack_voltage_changed.emit(v_pack)
                offset += 3
            elif marker == 0x84: # Current
                c_raw = int.from_bytes(data[offset+1:offset+3], "big")
                current = (c_raw & 0x7FFF) * 0.01
                if not (c_raw & 0x8000): current = -current
                self.state_store.pack_current_changed.emit(current)
                offset += 3
            elif marker == 0x85: # SOC
                self.state_store.soc_changed.emit(data[offset+1])
                offset += 2

            # --- TEMPÉRATURES ---
            elif marker == 0x80: # MOS Temp
                t = self._parse_temp(int.from_bytes(data[offset+1:offset+3], "big"))
                self.state_store.temp_mosfet.emit(t)
                offset += 3
            elif marker == 0x81: # T1
                t = self._parse_temp(int.from_bytes(data[offset+1:offset+3], "big"))
                self.state_store.temp_sensor_1.emit(t)
                offset += 3
            elif marker == 0x82: # T2
                t = self._parse_temp(int.from_bytes(data[offset+1:offset+3], "big"))
                self.state_store.temp_sensor_2.emit(t)
                offset += 3

            # --- STATS DE VIE ---
            elif marker == 0x87: # Cycle Count
                cycles = int.from_bytes(data[offset+1:offset+3], "big")
                self.state_store.cycle_count.emit(cycles)
                offset += 3
            elif marker == 0x89: # Total Capacity Ah
                cap = int.from_bytes(data[offset+1:offset+5], "big") * 0.001 # mAh to Ah
                offset += 5
            
            # --- ALERTES / STATUS ---
            elif marker == 0x8B: # Battery Status (MOSFET ON/OFF)
                status = int.from_bytes(data[offset+1:offset+3], "big")
                self.state_store.bms_status_bitmask.emit(status)
                offset += 3
            elif marker >= 0x90 and marker <= 0x96: # Alarms
                # On pourrait faire un tri précis ici
                offset += 2
                
            else:
                # Si on tombe sur un ID inconnu, on avance de 1 pour ne pas bloquer
                # (ou on pourrait sauter selon la taille fixe si connue)
                offset += 1

        # Après le scan, si on a des cellules, on calcule les stats
        if voltages:
            self.state_store.cell_voltages_changed.emit(voltages)
            v_min, v_max = min(voltages), max(voltages)
            self.state_store.cell_min_v.emit(v_min)
            self.state_store.cell_max_v.emit(v_max)
            self.state_store.cell_delta_v.emit(v_max - v_min)
            
            # Petit log de contrôle
            print(f"📊 [BMS] {len(voltages)} cells | V_max: {v_max:.3f}V | V_min: {v_min:.3f}V")

    def _parse_temp(self, val: int) -> float:
        """Décodage température JK BMS."""
        if val > 100:
            return float(-(val - 100))
        return float(val)