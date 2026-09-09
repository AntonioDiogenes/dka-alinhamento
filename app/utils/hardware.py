"""
Utilitário para identificação única do computador (app/utils/hardware.py).
Gera um HWID (Hardware ID) consistente baseado em atributos físicos do dispositivo.
"""
import hashlib
import platform
import subprocess
import uuid


def get_hardware_id() -> str:
    """
    Retorna um ID de hardware determinístico e único para o dispositivo atual.
    Tenta obter o UUID do sistema operacional/placa-mãe.
    Fallback para UUID baseado no MAC Address se o comando do SO falhar.
    """
    system_raw_id = ""
    system_name = platform.system()

    try:
        if system_name == "Windows":
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().split()
            if len(output) >= 2 and output[1].strip():
                system_raw_id = output[1].strip()
        elif system_name == "Linux":
            for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
                try:
                    with open(path, "r") as f:
                        content = f.read().strip()
                        if content:
                            system_raw_id = content
                            break
                except Exception:
                    pass
        elif system_name == "Darwin":  # macOS
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            for line in output.splitlines():
                if "IOPlatformUUID" in line:
                    system_raw_id = line.split("=")[-1].replace('"', "").strip()
                    break
    except Exception:
        system_raw_id = ""

    # Se a leitura falhou ou retornou nula/inválida, utiliza o nó MAC Address
    if not system_raw_id or system_raw_id.lower() in ["none", "unknown", "00000000-0000-0000-0000-000000000000"]:
        system_raw_id = f"mac-{uuid.getnode()}"

    # Gera hash SHA-256 truncado em blocos formatados
    formatted_id = hashlib.sha256(f"DKA-HWID-{system_raw_id}".encode("utf-8")).hexdigest()[:32].upper()
    return f"HWID-{formatted_id[:8]}-{formatted_id[8:16]}-{formatted_id[16:24]}-{formatted_id[24:32]}"
