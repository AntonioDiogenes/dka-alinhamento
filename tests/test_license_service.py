import unittest
from unittest.mock import patch, MagicMock
from app.utils.hardware import get_hardware_id
from app.services.license_service import validate_license


class TestLicenseService(unittest.TestCase):

    def test_get_hardware_id_returns_valid_string(self):
        hwid1 = get_hardware_id()
        hwid2 = get_hardware_id()

        self.assertTrue(hwid1.startswith("HWID-"))
        self.assertEqual(len(hwid1), 40)
        self.assertEqual(hwid1, hwid2, "HWID deve ser consistente para a mesma máquina")

    @patch("urllib.request.urlopen")
    def test_validate_license_includes_hardware_id(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"valid": true, "status": "active"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = validate_license("DKA-TEST-1234")

        self.assertTrue(result["valid"])
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        self.assertIn(b"hardware_id", req.data)


if __name__ == "__main__":
    unittest.main()
