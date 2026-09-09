"""
Modal de Seleção de Eixo (components/select_axle_modal.py).
Permite alternar interativamente o eixo em medição ativa.
"""
import tkinter as tk
from typing import List, Dict, Any, Callable
from app.utils.scroll_helper import setup_canvas_scrolling

class SelectAxleModal(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        axles_list: List[Dict[str, Any]],
        current_axle_id: str,
        on_select: Callable[[Dict[str, Any]], None],
        on_close: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, bg="#000000", **kwargs)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.axles_list = axles_list
        self.selected_axle = current_axle_id
        self.on_select = on_select
        self.on_close = on_close

        self._build_ui()

    def _build_ui(self):
        modal = tk.Frame(
            self,
            bg="#0d1117",
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=24,
            pady=20
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")

        hdr = tk.Frame(modal, bg="#0d1117")
        hdr.pack(fill="x", pady=(0, 14))

        lbl_title = tk.Label(
            hdr,
            text="SELECIONE O EIXO PARA MEDIÇÃO",
            font=("Segoe UI", 12, "bold"),
            fg="#FFFFFF",
            bg="#0d1117"
        )
        lbl_title.pack(side="left")

        btn_close_x = tk.Button(
            hdr,
            text=" ✕ ",
            font=("Segoe UI", 12, "bold"),
            fg="#9ca3af",
            bg="#0d1117",
            activebackground="#ef4444",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            command=self._close_modal
        )
        btn_close_x.pack(side="right")

        # Lista de Eixos Clicáveis (Rolável se mais de 4 eixos)
        num_axles = len(self.axles_list)
        if num_axles > 4:
            canvas_h = 240
            axles_canvas = tk.Canvas(modal, bg="#0d1117", height=canvas_h, highlightthickness=0, bd=0)
            axles_canvas.pack(fill="x", pady=(0, 16))
            axles_box = tk.Frame(axles_canvas, bg="#0d1117")
            axles_canvas.create_window((0, 0), window=axles_box, anchor="nw")
            axles_canvas.bind("<Configure>", lambda e: axles_canvas.itemconfig(axles_canvas.find_withtag("all")[0], width=e.width))
            axles_box.bind("<Configure>", lambda e: axles_canvas.configure(scrollregion=axles_canvas.bbox("all")))
            setup_canvas_scrolling(axles_canvas, axles_box)
        else:
            axles_box = tk.Frame(modal, bg="#0d1117")
            axles_box.pack(fill="x", pady=(0, 16))

        self.axle_buttons = {}

        for item in self.axles_list:
            axle_id = item["id"]
            axle_name = item["name"]
            is_steering = item.get("is_steering", False)

            is_sel = (axle_id == self.selected_axle)
            bg_col = "#162035" if is_sel else "#1a1f2e"
            fg_col = "#60a5fa" if is_sel else "#FFFFFF"
            border_col = "#4f77ff" if is_sel else "#2a3245"

            btn = tk.Button(
                axles_box,
                text=f"  [{axle_id}]  {axle_name} {'(Direcional)' if is_steering else '(Tração/Carreta)'}  ",
                font=("Segoe UI", 10, "bold"),
                fg=fg_col,
                bg=bg_col,
                activebackground="#2563eb",
                activeforeground="white",
                bd=1,
                highlightbackground=border_col,
                highlightthickness=1,
                padx=14,
                pady=8,
                cursor="hand2",
                command=lambda a_item=item: self._select_axle(a_item)
            )
            btn.pack(fill="x", pady=3)
            self.axle_buttons[axle_id] = btn

        # Botão Confirmar Seleção e Cancelar
        btn_bar = tk.Frame(modal, bg="#0d1117")
        btn_bar.pack(fill="x")

        btn_cancel = tk.Button(
            btn_bar,
            text="Cancelar",
            font=("Segoe UI", 10, "bold"),
            fg="#9ca3af",
            bg="#1a1f2e",
            activebackground="#2a3245",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._close_modal
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_confirm = tk.Button(
            btn_bar,
            text="Confirmar Seleção",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._confirm
        )
        btn_confirm.pack(side="right")

    def _select_axle(self, axle_item: Dict[str, Any]):
        self.selected_item = axle_item
        self.selected_axle = axle_item["id"]

        for a_id, btn in self.axle_buttons.items():
            is_sel = (a_id == self.selected_axle)
            btn.config(
                bg="#162035" if is_sel else "#1a1f2e",
                fg="#60a5fa" if is_sel else "#FFFFFF",
                highlightbackground="#4f77ff" if is_sel else "#2a3245"
            )

    def _confirm(self):
        item = getattr(self, "selected_item", None)
        if not item:
            for a in self.axles_list:
                if a["id"] == self.selected_axle:
                    item = a
                    break

        if item and self.on_select:
            self.on_select(item)
        self.destroy()

    def _close_modal(self):
        if self.on_close:
            try:
                self.on_close()
            except Exception:
                pass
        self.destroy()
