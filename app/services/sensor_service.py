"""
Serviço de Leitura e Comunicação dos Sensores Físicos DKA (app/services/sensor_service.py).
Baseado no protocolo do dka_monitor_2026.py (ASCII 112 bytes + CRLF na porta TCP 5000).

Mapeamento POS:
  0: DM (Dianteiro Motorista / Esquerda)
  1: DP (Dianteiro Passageiro / Direita)
  2: TM (Traseiro Motorista / Esquerda)
  3: TP (Traseiro Passageiro / Direita)
"""
import socket
import threading
import time
import random
from typing import Dict, Any, Optional, Callable, List

pos_names = {0: "DM", 1: "DP", 2: "TM", 3: "TP"}
pos_letter_map = {"1": 0, "2": 1, "3": 2, "4": 3}

def parse_ascii_packet(raw: bytes) -> Optional[Dict[str, Any]]:
    """
    Parser do protocolo ASCII de 112 bytes (dka_monitor_2026.py).
    Exemplo de pacote:
    [EP1CB-06.40CS-06.40CG+01.12NV-20.00KP+65.60IB-06.40IS-06.40IG+01.12FB-06.40FS-06.40FG+01.12BT100WF099IP011CM]
    """
    try:
        text = raw.decode('ascii', errors='ignore').strip()
        start = text.find('[')
        end = text.find(']')
        if start == -1 or end == -1 or end <= start:
            return None

        payload = text[start + 1:end].replace(',', '.')
        if len(payload) < 106:
            return None

        def field(tag: str, pos: int) -> float:
            label = payload[pos:pos+2]
            sign = payload[pos+2]
            value = payload[pos+3:pos+8]
            try:
                return float(sign + value)
            except ValueError:
                return 0.0

        origem = payload[0]
        pos_char = payload[2]
        pos_id = pos_letter_map.get(pos_char, -1)
        if pos_id == -1:
            return None

        camber     = field("CB", 3)
        caster     = field("CS", 11)
        conv       = field("CG", 19)
        nivel      = field("NV", 27)
        kpi        = field("KP", 35)
        ini_camber = field("IB", 43)
        ini_caster = field("IS", 51)
        ini_conv   = field("IG", 59)
        fin_camber = field("FB", 67)
        fin_caster = field("FS", 75)
        fin_conv   = field("FG", 83)

        batt      = int(payload[93:96])  if len(payload) >= 96 and payload[91:93] == "BT" else 100
        wifi      = int(payload[98:101]) if len(payload) >= 101 and payload[96:98] == "WF" else 99
        ip_suffix = payload[103:106]     if len(payload) >= 106 and payload[101:103] == "IP" else "011"
        ip_str    = f"10.10.10.{int(ip_suffix)}" if ip_suffix.isdigit() else "10.10.10.11"
        func      = payload[106:108]     if len(payload) >= 108 else "CM"

        return {
            "pos_id":     pos_id,
            "pos_nome":   pos_names.get(pos_id, "DM"),
            "conectado":  True,
            "origem":     origem,
            "camber":     camber,
            "caster":     caster,
            "conv":       conv,
            "nivel":      nivel,
            "kpi":        kpi,
            "ini_camber": ini_camber,
            "ini_caster": ini_caster,
            "ini_conv":   ini_conv,
            "fin_camber": fin_camber,
            "fin_caster": fin_caster,
            "fin_conv":   fin_conv,
            "batt":       batt,
            "wifi":       wifi,
            "ip":         ip_str,
            "func":       func,
            "raw":        text,
            "timestamp":  time.time()
        }
    except Exception as e:
        print(f"[SensorService] Erro parse: {e}")
        return None


class SensorService:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port
        self.running = False
        self.simulation_active = False

        # Estado dos 4 cabeçotes: 0 (DM), 1 (DP), 2 (TM), 3 (TP)
        self.heads_data: Dict[int, Optional[Dict[str, Any]]] = {
            0: None, 1: None, 2: None, 3: None
        }
        self.last_updates: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        self.listeners: List[Callable[[int, Dict[str, Any]], None]] = []

        self.server_socket: Optional[socket.socket] = None
        self.listen_thread: Optional[threading.Thread] = None
        self.sim_thread: Optional[threading.Thread] = None
        self.timeout_thread: Optional[threading.Thread] = None

    def add_listener(self, callback: Callable[[int, Dict[str, Any]], None]):
        """Adiciona um callback listener (pos_id, data_dict)."""
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback: Callable[[int, Dict[str, Any]], None]):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def _notify_listeners(self, pos_id: int, data: Dict[str, Any]):
        for listener in list(self.listeners):
            try:
                listener(pos_id, data)
            except Exception as e:
                print(f"[SensorService] Erro listener: {e}")

    def start_server(self):
        """Inicia o servidor de escuta TCP na porta 5000."""
        if self.running:
            return

        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        self.timeout_thread = threading.Thread(target=self._timeout_loop, daemon=True)
        self.timeout_thread.start()

    def stop_server(self):
        self.running = False
        self.simulation_active = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None

    def toggle_simulation(self, enable: Optional[bool] = None) -> bool:
        """Alterna ou define o modo de simulação."""
        if enable is None:
            self.simulation_active = not self.simulation_active
        else:
            self.simulation_active = enable

        if self.simulation_active and (self.sim_thread is None or not self.sim_thread.is_alive()):
            self.sim_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.sim_thread.start()

        return self.simulation_active

    def _listen_loop(self):
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.host, self.port))
            srv.listen(10)
            self.server_socket = srv
            print(f"[SensorService] Servidor TCP ouvindo em {self.host}:{self.port}")

            while self.running:
                try:
                    conn, addr = srv.accept()
                    threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
                except Exception:
                    if not self.running:
                        break
                    time.sleep(0.5)
        except Exception as e:
            print(f"[SensorService] Falha ao iniciar servidor TCP na porta {self.port}: {e}")

    def _handle_client(self, conn: socket.socket, addr):
        with conn:
            try:
                data = b""
                conn.settimeout(3.0)
                while self.running and len(data) < 200:
                    chunk = conn.recv(1)
                    if not chunk:
                        break
                    data += chunk
                    if data.endswith(b"\r\n") or data.endswith(b"]"):
                        break

                parsed = parse_ascii_packet(data)
                if parsed:
                    pos_id = parsed["pos_id"]
                    self.heads_data[pos_id] = parsed
                    self.last_updates[pos_id] = time.time()
                    self._notify_listeners(pos_id, parsed)
                    try:
                        conn.sendall(b"OK")
                    except Exception:
                        pass
            except Exception as e:
                pass

    def update_from_json(self, pos_data: Dict[str, Any]):
        """Permite injetar dados vindos da API JSON (FastAPI) diretamente."""
        pos_id = pos_data.get("pos_id", 0)
        pos_data["timestamp"] = time.time()
        self.heads_data[pos_id] = pos_data
        self.last_updates[pos_id] = time.time()
        self._notify_listeners(pos_id, pos_data)

    def _timeout_loop(self):
        while self.running:
            now = time.time()
            for pos_id in range(4):
                if self.last_updates[pos_id] > 0 and (now - self.last_updates[pos_id] > 3.5):
                    if not self.simulation_active:
                        self.last_updates[pos_id] = 0.0
                        if self.heads_data[pos_id]:
                            self.heads_data[pos_id]["conectado"] = False
                            self._notify_listeners(pos_id, self.heads_data[pos_id])
            time.sleep(1.0)

    def _simulation_loop(self):
        """Gera pacotes realistas em tempo real para os 4 cabeçotes quando em modo simulação."""
        base_values = {
            0: {"camber": 0.20, "caster": 2.50, "conv": 0.75, "kpi": 5.10, "ip": "10.10.10.11", "origem": "E"},
            1: {"camber": 0.25, "caster": 2.50, "conv": 0.75, "kpi": 5.10, "ip": "10.10.10.12", "origem": "S"},
            2: {"camber": 0.10, "caster": 0.00, "conv": 0.50, "kpi": 0.00, "ip": "10.10.10.13", "origem": "E"},
            3: {"camber": 0.10, "caster": 0.00, "conv": 0.50, "kpi": 0.00, "ip": "10.10.10.14", "origem": "S"},
        }

        while self.running and self.simulation_active:
            for pos_id in range(4):
                b = base_values[pos_id]
                noise = lambda: round(random.uniform(-0.03, 0.03), 2)

                data = {
                    "pos_id":     pos_id,
                    "pos_nome":   pos_names[pos_id],
                    "conectado":  True,
                    "origem":     b["origem"],
                    "camber":     round(b["camber"] + noise(), 2),
                    "caster":     round(b["caster"] + noise(), 2) if b["caster"] > 0 else 0.0,
                    "conv":       round(b["conv"] + noise(), 2),
                    "nivel":      round(random.uniform(-0.1, 0.1), 2),
                    "kpi":        round(b["kpi"] + noise(), 2) if b["kpi"] > 0 else 0.0,
                    "ini_camber": b["camber"],
                    "ini_caster": b["caster"],
                    "ini_conv":   b["conv"],
                    "fin_camber": b["camber"],
                    "fin_caster": b["caster"],
                    "fin_conv":   b["conv"],
                    "batt":       random.randint(90, 100),
                    "wifi":       random.randint(90, 99),
                    "ip":         b["ip"],
                    "func":       "CM",
                    "timestamp":  time.time()
                }
                self.heads_data[pos_id] = data
                self.last_updates[pos_id] = time.time()
                self._notify_listeners(pos_id, data)

            time.sleep(0.3)
