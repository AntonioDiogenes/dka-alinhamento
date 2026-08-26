"""
Layout Principal (MainWindow / ContentArea) da Aplicação Desktop.
"""
import tkinter as tk
from app.config.settings import COLORS
from app.core.router import Router

class MainLayout(tk.Frame):
    """
    Container raiz da interface da aplicação. Contém a ContentArea onde o Router
    substitui os Frames das telas dinamicamente.
    """
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.pack(fill="both", expand=True)

        # Content Area ocupando 100% do espaço da janela
        self.content_area = tk.Frame(self, bg=COLORS["bg_dark"])
        self.content_area.pack(fill="both", expand=True)

        # Inicializar o Roteador ligado a esta área de conteúdo
        self.router = Router(self.content_area)
