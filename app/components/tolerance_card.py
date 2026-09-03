"""
Cartão de Tolerância Inteligente com Arraste do Ponteiro (Drag & Drop) e Color-Coding Verde/Vermelho (components/tolerance_card.py).
Recursos:
- Permite puxar e arrastar o ponteiro (setinha) com o mouse para alterar a medição em tempo real.
- Coloração Dinâmica: Verde (#059669) dentro da tolerância de fábrica, Vermelho (#dc2626) fora da tolerância.
- Atualização em tempo real das posições das rodas.
"""
import tkinter as tk
from typing import Callable, Optional

class ToleranceCard(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: float = 0.75,
        min_tol: float = 0.49,
        max_tol: float = 1.00,
        unit: str = "mm",
        step: float = 0.01,
        on_change: Optional[Callable[[float], None]] = None,
        read_only: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            height=110,
            highlightthickness=1,
            padx=10,
            pady=8,
            **kwargs
        )
        self.pack_propagate(False)

        self.title = title
        self.value = value
        self.min_tol = min_tol
        self.max_tol = max_tol
        self.unit = unit
        self.step = step
        self.on_change = on_change
        self.read_only = read_only
        self.is_editing = False

        self._build_ui()
        self._update_color_and_state()

    def _build_ui(self):
        # 1. Linha Superior: Badges MÍN e MÁX de Tolerância
        top_line = tk.Frame(self, bg=self["bg"])
        top_line.pack(fill="x")

        self.lbl_min_badge = tk.Label(
            top_line,
            text=f"MÍN {self._format_num(self.min_tol)}",
            font=("Segoe UI", 8, "bold"),
            fg="#60a5fa",
            bg="#0f172a",
            padx=6,
            pady=1
        )
        self.lbl_min_badge.pack(side="left")

        self.lbl_title = tk.Label(
            top_line,
            text=self.title.upper(),
            font=("Segoe UI", 8, "bold"),
            fg="#ffffff",
            bg=self["bg"]
        )
        self.lbl_title.pack(side="left", expand=True)

        self.lbl_max_badge = tk.Label(
            top_line,
            text=f"MÁX {self._format_num(self.max_tol)}",
            font=("Segoe UI", 8, "bold"),
            fg="#60a5fa",
            bg="#0f172a",
            padx=6,
            pady=1
        )
        self.lbl_max_badge.pack(side="right")

        # 2. Container Central de Valor e Botões
        box = tk.Frame(self, bg=self["bg"])
        box.pack(expand=True, fill="x", pady=(2, 0))

        btn_dec = tk.Button(
            box,
            text="‹",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg=self["bg"],
            activebackground="#000000",
            activeforeground="white",
            bd=0,
            padx=6,
            cursor="hand2",
            command=self._decrement
        )
        btn_dec.pack(side="left")

        self.lbl_value = tk.Label(
            box,
            text=self._format_value(),
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg=self["bg"],
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

        btn_inc = tk.Button(
            box,
            text="›",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg=self["bg"],
            activebackground="#000000",
            activeforeground="white",
            bd=0,
            padx=6,
            cursor="hand2",
            command=self._increment
        )
        btn_inc.pack(side="right")

        # 3. Canvas Gauge de Tolerância (Ponteiro Deslizante / Drag & Drop)
        self.gauge_canvas = tk.Canvas(self, height=12, bg="#0f172a", highlightthickness=1, highlightbackground="#334155", bd=0, cursor="hand2")
        self.gauge_canvas.pack(fill="x", side="bottom", pady=(2, 0))

        # Eventos de Arraste (Drag & Drop) e Redimensionamento de Tela
        self.gauge_canvas.bind("<Configure>", lambda e: self._draw_gauge())
        self.gauge_canvas.bind("<Button-1>", self._on_gauge_drag)
        self.gauge_canvas.bind("<B1-Motion>", self._on_gauge_drag)
        self.gauge_canvas.bind("<ButtonRelease-1>", self._on_gauge_drag)

    def set_read_only(self, read_only: bool):
        self.read_only = read_only

    def _on_gauge_drag(self, event):
        """Permite puxar e arrastar o ponteiro (setinha) para alterar o valor da medição."""
        if self.read_only:
            return
        w = max(self.gauge_canvas.winfo_width(), 200)
        x = max(6, min(w - 6, event.x))
        rel_pos = (x - 6) / max(1, (w - 12))

        span = max(self.max_tol - self.min_tol, 0.2)
        min_val = self.min_tol - (span * 0.4)
        max_val = self.max_tol + (span * 0.4)

        new_val = min_val + rel_pos * (max_val - min_val)
        self.update_value(new_val)
        if self.on_change:
            self.on_change(self.value)

    def _format_num(self, val: float) -> str:
        prefix = "+" if val >= 0 else ""
        return f"{prefix}{val:.2f} {self.unit}".replace(".", ",")

    def _format_value(self) -> str:
        return self._format_num(self.value)

    def _update_color_and_state(self):
        is_ok = (self.min_tol <= self.value <= self.max_tol)
        card_bg = "#059669" if is_ok else "#dc2626"
        border_col = "#10b981" if is_ok else "#ef4444"

        self.config(bg=card_bg, highlightbackground=border_col)
        self.lbl_title.config(bg=card_bg)
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(bg=card_bg)
                for cw in w.winfo_children():
                    if isinstance(cw, tk.Label):
                        if cw not in [self.lbl_min_badge, self.lbl_max_badge]:
                            cw.config(bg=card_bg)
                    elif isinstance(cw, tk.Button):
                        cw.config(bg=card_bg)

        self._draw_gauge()

    def _draw_gauge(self):
        self.gauge_canvas.delete("all")
        w = max(self.gauge_canvas.winfo_width(), 200)

        span = max(self.max_tol - self.min_tol, 0.2)
        min_val = self.min_tol - (span * 0.4)
        max_val = self.max_tol + (span * 0.4)
        val_span = max_val - min_val

        rel_pos = (self.value - min_val) / val_span
        rel_pos = max(0.0, min(1.0, rel_pos))

        pointer_x = int(rel_pos * (w - 12)) + 6

        # Desenhar linha central de referência
        self.gauge_canvas.create_line(6, 6, w - 6, 6, fill="#475569", width=2)

        # Desenhar seta/ponteiro triangular amarelo brilhante
        self.gauge_canvas.create_polygon(
            pointer_x - 6, 0,
            pointer_x + 6, 0,
            pointer_x, 11,
            fill="#f59e0b", outline="#ffffff", width=1
        )

    def update_value(self, new_val: float):
        self.value = round(new_val, 2)
        self.lbl_value.config(text=self._format_value())
        self._update_color_and_state()

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
