"""
Configurações globais da aplicação.
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = APP_DIR / "assets"

# Tema de Cores (Dark Theme)
COLORS = {
    "bg_dark": "#111520",        # Fundo imersivo escuro padrão
    "bg_card": "#1c2230",        # Fundo de containers/cards secundários
    "bg_card_translucent": "#151a26", # Fundo translúcido para navcards
    "border_subtle": "#2a3245",   # Borda sutil suave
    "border_white_soft": "#ffffff66", # Borda branca translúcida
    "accent_blue": "#4f77ff",    # Azul elétrico vibrante (Hover / Active)
    "accent_blue_hover": "#6085ff",
    "text_white": "#ffffff",
    "text_muted": "#8a94a6",      # Cinza claro para rótulos secundários
    "text_gray": "#6b7280",       # text-gray-500
    "danger": "#ef4444",          # Vermelho para ações destrutivas (Remover fundo)
}

FONTS = {
    "title_clock": ("Segoe UI", 64, "bold"), # Relógio gigante estilo 64px
    "header_title": ("Segoe UI", 16, "bold"),
    "sublabel": ("Segoe UI", 9, "bold"),
    "card_title": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 11),
    "button": ("Segoe UI", 10, "bold"),
}

# Dados de Unidades de Oficina Mockadas (Seletor)
MOCK_UNIDADES = [
    {"id": 1, "nome": "Oficina Matriz - São Paulo"},
    {"id": 2, "nome": "Oficina Filial - Rio de Janeiro"},
    {"id": 3, "nome": "Oficina Filial - Curitiba"},
]

class AppState:
    """Estado global mutável da aplicação em tempo de execução."""
    def __init__(self):
        self.active_unit = MOCK_UNIDADES[0]
        self.unidades = MOCK_UNIDADES
        self.custom_bg_path = None

state = AppState()
