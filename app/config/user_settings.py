"""
Gerenciador de Configurações Persistentes do Usuário (config/user_settings.py).
Salva e carrega preferências (ex: caminho da imagem de fundo personalizada).
"""
import json
from pathlib import Path
from typing import Dict, Any

SETTINGS_FILE = Path.home() / ".dka_user_settings.json"

def load_user_settings() -> Dict[str, Any]:
    """Carrega as configurações salvas do usuário."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Erro ao carregar configurações do usuário:", e)
    return {}

def save_user_settings(settings: Dict[str, Any]) -> bool:
    """Salva o dicionário de configurações no arquivo JSON do usuário."""
    try:
        current = load_user_settings()
        current.update(settings)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("Erro ao salvar configurações do usuário:", e)
        return False
