import time
import unittest
from app.services.sensor_service import parse_ascii_packet, SensorService

class TestSensorService(unittest.TestCase):
    def test_parse_ascii_packet(self):
        # Pacote de teste conforme o protocolo do dka_monitor_2026.py
        raw = b"[EP1CB-06.40CS-06.40CG+01.12NV-20.00KP+65.60IB-06.40IS-06.40IG+01.12FB-06.40FS-06.40FG+01.12BT100WF099IP011CM]\r\n"
        data = parse_ascii_packet(raw)

        self.assertIsNotNone(data)
        self.assertEqual(data["pos_id"], 0)  # 1 -> DM (pos_id 0)
        self.assertEqual(data["origem"], "E")
        self.assertEqual(data["camber"], -6.40)
        self.assertEqual(data["caster"], -6.40)
        self.assertEqual(data["conv"], 1.12)
        self.assertEqual(data["nivel"], -20.00)
        self.assertEqual(data["kpi"], 65.60)
        self.assertEqual(data["batt"], 100)
        self.assertEqual(data["wifi"], 99)
        self.assertEqual(data["ip"], "10.10.10.11")
        self.assertEqual(data["func"], "CM")

    def test_sensor_service_simulation(self):
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

        self.assertGreater(len(received_packets), 0)
        pos_id, first_pkt = received_packets[0]
        self.assertTrue(0 <= pos_id <= 3)
        self.assertIn("camber", first_pkt)
        self.assertIn("conv", first_pkt)

if __name__ == "__main__":
    unittest.main()
