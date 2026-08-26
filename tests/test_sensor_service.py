import time
from app.services.sensor_service import parse_ascii_packet, SensorService

def test_parse_ascii_packet():
    # Pacote de teste conforme o protocolo do dka_monitor_2026.py
    raw = b"[EP1CB-06.40CS-06.40CG+01.12NV-20.00KP+65.60IB-06.40IS-06.40IG+01.12FB-06.40FS-06.40FG+01.12BT100WF099IP011CM]\r\n"
    data = parse_ascii_packet(raw)

    assert data is not None
    assert data["pos_id"] == 0  # 1 -> DM (pos_id 0)
    assert data["origem"] == "E"
    assert data["camber"] == -6.40
    assert data["caster"] == -6.40
    assert data["conv"] == 1.12
    assert data["nivel"] == -20.00
    assert data["kpi"] == 65.60
    assert data["batt"] == 100
    assert data["wifi"] == 99
    assert data["ip"] == "10.10.10.11"
    assert data["func"] == "CM"

def test_sensor_service_simulation():
    service = SensorService.get_instance()
    received_packets = []

    def callback(pos_id, data):
        received_packets.append((pos_id, data))

    service.add_listener(callback)
    service.start_server()
    service.toggle_simulation(True)

    time.sleep(1.0)

    service.toggle_simulation(False)
    service.remove_listener(callback)

    assert len(received_packets) > 0
    pos_id, first_pkt = received_packets[0]
    assert 0 <= pos_id <= 3
    assert "camber" in first_pkt
    assert "conv" in first_pkt

if __name__ == "__main__":
    test_parse_ascii_packet()
    test_sensor_service_simulation()
    print("✅ Todos os testes de sensor passaram com sucesso!")
