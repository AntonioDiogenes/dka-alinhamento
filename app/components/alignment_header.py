"""
Cabeçalho Especializado de Alinhamento (components/alignment_header.py).
Estilo: Fundo azul-marinho profundo bg-[#001f3f], altura 64px, título "Alinhamento • Selecione o truck", botões de voltar (<-) e fechar (X).
"""
import tkinter as tk
from typing import Callable, Optional
from app.utils.icons import create_icon_image

class AlignmentHeader(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Alinhamento",
        subtitle: str = "Selecione o truck",
        on_back: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        bg_navy = "#001f3f"
        super().__init__(
            parent,
            bg=bg_navy,
            height=64,
            padx=20,
            highlightbackground="#002d5c",
            highlightthickness=1,
            **kwargs
        )
        self.pack_propagate(False)

        self.on_back = on_back
        self.on_close = on_close

        self.img_back = create_icon_image("arrow_left", size=22, color="#FFFFFF")
        self.img_close = create_icon_image("x", size=22, color="#FFFFFF")

        # 1. Canto Esquerdo — Ícone Seta Voltar em botão circular
        btn_back = tk.Button(
            self,
            image=self.img_back,
            bg=bg_navy,
            activebackground="#003366",
            bd=0,
            padx=8,
            pady=8,
            cursor="hand2",
            command=self._handle_back
        )
        btn_back.pack(side="left")

        # 2. Centro — Título e Subtítulo
        center_frame = tk.Frame(self, bg=bg_navy)
        center_frame.pack(side="left", padx=16)

        lbl_title = tk.Label(
            center_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            fg="#FFFFFF",
            bg=bg_navy
        )
        lbl_title.pack(side="left")

        lbl_dot = tk.Label(
            center_frame,
            text="  •  ",
            font=("Segoe UI", 11, "bold"),
            fg="#60a5fa",
            bg=bg_navy
        )
        lbl_dot.pack(side="left")

        lbl_sub = tk.Label(
            center_frame,
            text=subtitle,
            font=("Segoe UI", 10),
            fg="#d1d5db",
            bg=bg_navy
        )
        lbl_sub.pack(side="left")

        # 3. Canto Direito — Ícone Fechar (X)
        btn_close = tk.Button(
            self,
            image=self.img_close,
            bg=bg_navy,
            activebackground="#003366",
            bd=0,
            padx=8,
            pady=8,
            cursor="hand2",
            command=self._handle_close
        )
        btn_close.pack(side="right")

    def _handle_back(self):
        if self.on_back:
            self.on_back()

    def _handle_close(self):
        if self.on_close:
            self.on_close()
