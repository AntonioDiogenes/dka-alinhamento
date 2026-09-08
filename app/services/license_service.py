"""
Serviço de Validação de Licença (services/license_service.py).
Responsabilidades:
  - Fazer POST em https://dka.cea.eti.br/api/licenses/validate
  - Retornar o dicionário JSON da resposta
  - Lançar LicenseNetworkError em caso de falha de rede/HTTP
"""
import json
import urllib.request
from app.utils.http import urlopen_with_ssl

VALIDATE_URL = "https://dka.cea.eti.br/api/licenses/validate"
PRODUCT_NAME = "Sistema Tkinter Desktop"


class LicenseNetworkError(Exception):
    """Erro de rede/HTTP ao tentar validar a licença."""


def validate_license(serial_key: str) -> dict:
    """
    Valida a chave serial contra o servidor de licenças.

    Retorna o JSON completo da API, por exemplo:
        {
            "valid": True,
            "status": "active",
            "message": "...",
            "data": {"days_remaining": 365, "client": {"name": "..."}}
        }

    Lança:
        LicenseNetworkError — se houver falha de rede, timeout ou status HTTP != 200.
    """
    payload = json.dumps({
        "serial_key": serial_key.strip(),
        "product": PRODUCT_NAME,
    }).encode("utf-8")

    req = urllib.request.Request(
        VALIDATE_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DKA-Alinhamento-Desktop/1.0",
        },
    )

    try:
        with urlopen_with_ssl(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        # Tenta extrair a mensagem de erro do corpo da resposta
        try:
            body = json.loads(exc.read().decode("utf-8"))
            return body  # Pode conter {"valid": false, "message": "..."}
        except Exception:
            raise LicenseNetworkError(
                f"Erro HTTP {exc.code}: {exc.reason}"
            ) from exc
    except Exception as exc:
        raise LicenseNetworkError(
            f"Falha de conexão ao validar licença: {exc}"
        ) from exc
