"""
Tela 2: Criação de Cliente (views/clientes/create.py).
Renderiza o formulário reutilizável ClientForm em layout escuro alinhado com o sistema.
"""
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any

from app.config.settings import COLORS
from app.services.client_service import ClientService
from app.components.client_form import ClientForm
from app.utils.icons import create_icon_image
from app.utils.scroll_helper import setup_canvas_scrolling

class ClientCreateView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.router = router
        self.img_back = create_icon_image("arrow_left", size=20, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # Cabeçalho Superior (AlignmentHeader Dark)
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
            text="Novo Cliente",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_dark"]
        )
        lbl_title.pack(side="left")

        # Container Principal com Canvas Rolável
        self.main_area = tk.Frame(self, bg=COLORS["bg_dark"], padx=32, pady=24)
        self.main_area.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_area, bg=COLORS["bg_dark"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.form = ClientForm(
            self.canvas,
            client_data=None,
            read_only=False,
            on_save=self._on_save,
            on_cancel=self._on_cancel
        )
        self.canvas.create_window((0, 0), window=self.form, anchor="nw")
        self.form.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))
        setup_canvas_scrolling(self.canvas, self.form)

    def _on_save(self, data: Dict[str, Any]):
        saved = ClientService.save_client(data)
        messagebox.showinfo("Sucesso", f"Cliente '{saved['nome']}' cadastrado com sucesso!")
        self.router.navigate("clientes.index")

    def _on_cancel(self):
        self.router.navigate("clientes.index")
