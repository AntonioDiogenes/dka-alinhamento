"""
Componente Card de Caminhão Bicolor (components/truck_card.py).
Design:
- Altura 128px (h-32), cantos arredondados, transição e hover border azul (#4f77ff).
- Lado Esquerdo (1/3): Fundo branco absoluto bg-white com Badge de 3 Letras da marca e Nome do Fabricante.
- Lado Direito (2/3): Fundo Grafite Escuro bg-[#2c2c2c] com Rótulo TRUCK, Nome do Modelo e Indicador de Aro (• 22).
"""
import tkinter as tk
from typing import Callable, Dict, Any

class TruckCard(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        truck_data: Dict[str, Any],
        on_click: Callable[[Dict[str, Any]], None],
        **kwargs
    ):
        self.truck_data = truck_data
        self.on_click = on_click

        super().__init__(
            parent,
            bg="#2c2c2c",
            width=320,
            height=128,
            highlightbackground="#3b4252",
            highlightthickness=1,
            cursor="hand2",
            **kwargs
        )
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1, uniform="card_col") # Lado Esquerdo (1/3)
        self.grid_columnconfigure(1, weight=2, uniform="card_col") # Lado Direito (2/3)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()
        self._bind_hover_and_click()

    def _build_ui(self):
        brand_code = self.truck_data.get("brand_code", "TRK")
        brand_name = self.truck_data.get("brand_name", "Marca")
        category = self.truck_data.get("category", "VEÍCULO")
        if category == "TRUCK":
            category = "VEÍCULO"
        model_name = self.truck_data.get("model_name", "Modelo")
        rim_size = self.truck_data.get("rim_size", "22")

        # ==========================================
        # LADO ESQUERDO (1/3) — FUNDO BRANCO ABSOLUTO
        # ==========================================
        self.left_box = tk.Frame(self, bg="#ffffff", padx=12, pady=12)
        self.left_box.grid(row=0, column=0, sticky="nsew")

        # Inner container para centralização vertical
        left_inner = tk.Frame(self.left_box, bg="#ffffff")
        left_inner.pack(expand=True)

        # Badge 3 Letras (ex: VOL, SCA, MER)
        self.badge_frame = tk.Frame(left_inner, bg="#e2e8f0", padx=10, pady=4, highlightbackground="#cbd5e1", highlightthickness=1)
        self.badge_frame.pack(pady=(0, 6))

        self.lbl_badge = tk.Label(
            self.badge_frame,
            text=brand_code,
            font=("Segoe UI", 9, "bold"),
            fg="#1e293b",
            bg="#e2e8f0"
        )
        self.lbl_badge.pack()

        # Nome do Fabricante
        self.lbl_brand = tk.Label(
            left_inner,
            text=brand_name,
            font=("Segoe UI", 9, "bold"),
            fg="#374151",
            bg="#ffffff"
        )
        self.lbl_brand.pack()

        # ==========================================
        # LADO DIREITO (2/3) — FUNDO GRAFITE ESCURO (#2c2c2c)
        # ==========================================
        self.right_box = tk.Frame(self, bg="#2c2c2c", padx=16, pady=14)
        self.right_box.grid(row=0, column=1, sticky="nsew")

        # Rótulo Categoria TRUCK
        self.lbl_cat = tk.Label(
            self.right_box,
            text=category,
            font=("Segoe UI", 8, "bold"),
            fg="#9ca3af",
            bg="#2c2c2c",
            anchor="w"
        )
        self.lbl_cat.pack(anchor="w")

        # Nome do Modelo
        self.lbl_model = tk.Label(
            self.right_box,
            text=model_name,
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg="#2c2c2c",
            anchor="w",
            wraplength=220,
            justify="left"
        )
        self.lbl_model.pack(anchor="w", pady=(2, 0))

        # Indicador de Aro no Canto Inferior Direito (• 22)
        bot_frame = tk.Frame(self.right_box, bg="#2c2c2c")
        bot_frame.pack(fill="x", side="bottom")

        self.lbl_rim = tk.Label(
            bot_frame,
            text=f"• {rim_size}",
            font=("Segoe UI", 10, "bold"),
            fg="#60a5fa",
            bg="#2c2c2c"
        )
        self.lbl_rim.pack(side="right")

    def _bind_hover_and_click(self):
        """Associa efeitos de hover e clique para todos os widgets filhos do card."""
        widgets = [
            self, self.left_box, self.right_box, self.badge_frame,
            self.lbl_badge, self.lbl_brand, self.lbl_cat, self.lbl_model, self.lbl_rim
        ]

        def on_enter(e):
            self.config(highlightbackground="#4f77ff", highlightthickness=2)
            self.right_box.config(bg="#343a46")

        def on_leave(e):
            self.config(highlightbackground="#3b4252", highlightthickness=1)
            self.right_box.config(bg="#2c2c2c")

        def on_click_event(e):
            if self.on_click:
                self.on_click(self.truck_data)

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click_event)
