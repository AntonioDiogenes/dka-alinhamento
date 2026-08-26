"""
Tela 4: Visualização de Cliente (views/clientes/show.py).
Renderiza ClientForm em modo Somente Leitura (readOnly=True) e o Histórico de Atendimentos do Cliente.
"""
import tkinter as tk
from typing import Dict, Any

from app.config.settings import COLORS
from app.services.client_service import ClientService
from app.components.client_form import ClientForm
from app.components.client_attendance_history import ClientAttendanceHistory
from app.utils.icons import create_icon_image

class ClientShowView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        kwargs = kwargs or {}
        self.client_id = kwargs.get("client_id", 1)

        super().__init__(parent, bg=COLORS["bg_dark"])
        self.router = router

        self.client_data = ClientService.get_client_by_id(self.client_id) or {}
        self.attendances = ClientService.get_client_attendances(self.client_id)
        self.img_back = create_icon_image("arrow_left", size=20, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # Cabeçalho Superior
        self.header = tk.Frame(
            self,
            bg=COLORS["bg_dark"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=28,
            pady=16
        )
        self.header.pack(fill="x", side="top")

        btn_back = tk.Button(
            self.header,
            image=self.img_back,
            bg=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"],
            bd=0,
            cursor="hand2",
            command=lambda: self.router.navigate("clientes.index")
        )
        btn_back.pack(side="left", padx=(0, 16))

        lbl_title = tk.Label(
            self.header,
            text=f"Visualizar Cliente — {self.client_data.get('nome', '')}",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_dark"]
        )
        lbl_title.pack(side="left")

        # Container Rolável
        self.canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=32, pady=20)

        self.scroll_frame = tk.Frame(self.canvas, bg=COLORS["bg_dark"])
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        # 1. Formulário em Modo Somente Leitura (readOnly=True)
        self.form = ClientForm(
            self.scroll_frame,
            client_data=self.client_data,
            read_only=True,
            on_cancel=self._on_cancel
        )
        self.form.pack(fill="x", pady=(0, 24))

        # 2. Seção Integrada: Histórico de Atendimentos do Cliente
        self.history_section = ClientAttendanceHistory(
            self.scroll_frame,
            attendances=self.attendances
        )
        self.history_section.pack(fill="x")

    def _on_cancel(self):
        self.router.navigate("clientes.index")
