"""
Componente Contador de Eixos (components/axle_counter.py).
Botões (-) e (+) em azul com display centralizado de número gigante.
"""
import tkinter as tk
from typing import Callable

class AxleCounter(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        label_text: str,
        value: int,
        min_value: int = 1,
        max_value: int = 5,
        on_change: Callable[[int], None] = None,
        **kwargs
    ):
        super().__init__(parent, bg="#1a1f2e", **kwargs)

        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.on_change = on_change

        self._build_ui(label_text)

    def _build_ui(self, label_text: str):
        lbl = tk.Label(
            self,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            fg="#d1d5db",
            bg="#1a1f2e"
        )
        lbl.pack(anchor="w", pady=(0, 6))

        box = tk.Frame(self, bg="#1a1f2e")
        box.pack(anchor="w")

        # Botão Subtrair (-)
        self.btn_minus = tk.Button(
            box,
            text="-",
            font=("Segoe UI", 16, "bold"),
            fg="#60a5fa",
            bg="#162035",
            activebackground="#2563eb",
            activeforeground="white",
            bd=1,
            highlightbackground="#2563eb",
            highlightthickness=1,
            width=3,
            height=1,
            cursor="hand2",
            command=self._decrement
        )
        self.btn_minus.pack(side="left", padx=(0, 6))

        # Display do Valor
        self.val_box = tk.Frame(box, bg="#0d1117", highlightbackground="#2a3245", highlightthickness=1, padx=16, pady=4)
        self.val_box.pack(side="left", padx=(0, 6))

        self.lbl_value = tk.Label(
            self.val_box,
            text=str(self.value),
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#0d1117",
            width=2
        )
        self.lbl_value.pack()

        # Botão Adicionar (+)
        self.btn_plus = tk.Button(
            box,
            text="+",
            font=("Segoe UI", 16, "bold"),
            fg="#60a5fa",
            bg="#162035",
            activebackground="#2563eb",
            activeforeground="white",
            bd=1,
            highlightbackground="#2563eb",
            highlightthickness=1,
            width=3,
            height=1,
            cursor="hand2",
            command=self._increment
        )
        self.btn_plus.pack(side="left")

        self._update_buttons_state()

    def _decrement(self):
        if self.value > self.min_value:
            self.value -= 1
            self.lbl_value.config(text=str(self.value))
            self._update_buttons_state()
            if self.on_change:
                self.on_change(self.value)

    def _increment(self):
        if self.value < self.max_value:
            self.value += 1
            self.lbl_value.config(text=str(self.value))
            self._update_buttons_state()
            if self.on_change:
                self.on_change(self.value)

    def _update_buttons_state(self):
        if self.value <= self.min_value:
            self.btn_minus.config(state="disabled", fg="#4b5563", bg="#0d1117")
        else:
            self.btn_minus.config(state="normal", fg="#60a5fa", bg="#162035")

        if self.value >= self.max_value:
            self.btn_plus.config(state="disabled", fg="#4b5563", bg="#0d1117")
        else:
            self.btn_plus.config(state="normal", fg="#60a5fa", bg="#162035")
