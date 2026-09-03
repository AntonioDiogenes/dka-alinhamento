"""
Cartão de Medição Direta sem Tolerância (components/measurement_card.py).
Usado para medidas lineares puras (Reta Frente Esq, Total, Dir, Distância Entre Eixos, Ângulo de Impulso).
Recursos:
- Fundo escuro azulado #1e293b.
- Ajuste por botões < e > (incremento 0.01).
- Digitação direta no teclado numérico ao clicar sobre o número gigante.
"""
import tkinter as tk
from typing import Callable, Optional

class MeasurementCard(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: float = 0.0,
        unit: str = "mm",
        step: float = 0.01,
        on_change: Optional[Callable[[float], None]] = None,
        read_only: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            bg="#1e293b",
            height=110,
            highlightbackground="#334155",
            highlightthickness=1,
            padx=12,
            pady=10,
            **kwargs
        )
        self.pack_propagate(False)

        self.title = title
        self.value = value
        self.unit = unit
        self.step = step
        self.on_change = on_change
        self.read_only = read_only
        self.is_editing = False

        self._build_ui()

    def _build_ui(self):
        # Título Superior
        lbl_title = tk.Label(
            self,
            text=self.title.upper(),
            font=("Segoe UI", 8, "bold"),
            fg="#94a3b8",
            bg="#1e293b"
        )
        lbl_title.pack(anchor="n")

        # Container Principal de Valor e Ajuste
        box = tk.Frame(self, bg="#1e293b")
        box.pack(expand=True, fill="x", pady=(4, 0))

        # Botão Decrementar (<)
        self.btn_dec = tk.Button(
            box,
            text="‹",
            font=("Segoe UI", 16, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            activebackground="#334155",
            activeforeground="white",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._decrement
        )
        self.btn_dec.pack(side="left")

        # Label/Entry Central de Valor
        self.lbl_value = tk.Label(
            box,
            text=self._format_value(),
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#1e293b",
            cursor="xterm"
        )
        self.lbl_value.pack(side="left", expand=True)
        self.lbl_value.bind("<Button-1>", self._enable_entry)

        self.entry_value = tk.Entry(
            box,
            font=("Segoe UI", 18, "bold"),
            fg="#60a5fa",
            bg="#0f172a",
            insertbackground="white",
            bd=1,
            justify="center"
        )
        self.entry_value.bind("<Return>", self._save_entry)
        self.entry_value.bind("<FocusOut>", self._save_entry)

        # Botão Incrementar (>)
        self.btn_inc = tk.Button(
            box,
            text="›",
            font=("Segoe UI", 16, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            activebackground="#334155",
            activeforeground="white",
            bd=0,
            padx=8,
            cursor="hand2",
            command=self._increment
        )
        self.btn_inc.pack(side="right")

    def _format_value(self) -> str:
        prefix = "+" if self.value >= 0 else ""
        return f"{prefix}{self.value:.2f} {self.unit}".replace(".", ",")

    def set_read_only(self, read_only: bool):
        self.read_only = read_only
        cursor = "arrow" if read_only else "hand2"
        self.btn_dec.config(cursor=cursor)
        self.btn_inc.config(cursor=cursor)

    def update_value(self, new_val: float):
        self.value = round(new_val, 2)
        self.lbl_value.config(text=self._format_value())

    def _decrement(self):
        if self.read_only:
            return
        self.update_value(self.value - self.step)
        if self.on_change:
            self.on_change(self.value)

    def _increment(self):
        if self.read_only:
            return
        self.update_value(self.value + self.step)
        if self.on_change:
            self.on_change(self.value)

    def _enable_entry(self, event=None):
        if self.read_only or self.is_editing:
            return
        self.is_editing = True
        self.lbl_value.pack_forget()
        self.entry_value.delete(0, tk.END)
        self.entry_value.insert(0, f"{self.value:.2f}".replace(".", ","))
        self.entry_value.pack(side="left", expand=True)
        self.entry_value.focus_set()

    def _save_entry(self, event=None):
        if not self.is_editing:
            return
        raw = self.entry_value.get().replace(",", ".").strip()
        try:
            val = float(raw)
            self.update_value(val)
            if self.on_change:
                self.on_change(self.value)
        except ValueError:
            pass

        self.entry_value.pack_forget()
        self.lbl_value.pack(side="left", expand=True)
        self.is_editing = False
