"""
Seção Integrada: Histórico de Atendimentos do Cliente (components/client_attendance_history.py).
Exibida na tela de Edição/Visualização do Cliente.
"""
import os
import webbrowser
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any

from app.config.settings import COLORS
from app.utils.icons import create_icon_image
from app.utils.pdf_generator import generate_alignment_pdf

class ClientAttendanceHistory(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        attendances: List[Dict[str, Any]],
        **kwargs
    ):
        bg_color = "#1a1f2e"
        fg_color = "#ffffff"
        border_color = "#2a3245"

        super().__init__(
            parent,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=24,
            pady=20,
            **kwargs
        )

        self.attendances = attendances
        self.bg_color = bg_color
        self.fg_color = fg_color

        # Ícones
        self.img_clipboard = create_icon_image("clipboard_list", size=22, color="#60a5fa")
        self.img_cal = create_icon_image("calendar", size=16, color="#9ca3af")
        self.img_wrench = create_icon_image("wrench", size=16, color="#9ca3af")
        self.img_eye = create_icon_image("eye", size=16, color="#60a5fa")

        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=self.bg_color)
        hdr.pack(fill="x", pady=(0, 16))

        lbl_icon = tk.Label(hdr, image=self.img_clipboard, bg=self.bg_color)
        lbl_icon.pack(side="left", padx=(0, 10))

        lbl_title = tk.Label(
            hdr,
            text="Histórico de Atendimentos",
            font=("Segoe UI", 12, "bold"),
            fg=self.fg_color,
            bg=self.bg_color
        )
        lbl_title.pack(side="left")

        divider = tk.Frame(self, bg="#2a3245", height=1)
        divider.pack(fill="x", pady=(0, 16))

        if not self.attendances:
            lbl_empty = tk.Label(
                self,
                text="Nenhum atendimento registrado para este cliente.",
                font=("Segoe UI", 10, "italic"),
                fg="#9ca3af",
                bg=self.bg_color,
                pady=16
            )
            lbl_empty.pack(anchor="w")
            return

        for att in self.attendances:
            card = tk.Frame(
                self,
                bg="#0d1117",
                highlightbackground="#2a3245",
                highlightthickness=1,
                padx=16,
                pady=12
            )
            card.pack(fill="x", pady=6)

            top_line = tk.Frame(card, bg="#0d1117")
            top_line.pack(fill="x")

            lbl_id = tk.Label(
                top_line,
                text=f"#{att['id']}",
                font=("Segoe UI", 10, "bold"),
                fg="#60a5fa",
                bg="#0d1117"
            )
            lbl_id.pack(side="left", padx=(0, 8))

            lbl_title = tk.Label(
                top_line,
                text=att["title"],
                font=("Segoe UI", 10, "bold"),
                fg=self.fg_color,
                bg="#0d1117"
            )
            lbl_title.pack(side="left")

            badge_color = att.get("status_color", "#10b981")
            lbl_badge = tk.Label(
                top_line,
                text=f"  {att['status']}  ",
                font=("Segoe UI", 8, "bold"),
                fg="white",
                bg=badge_color,
                padx=6,
                pady=2
            )
            lbl_badge.pack(side="right")

            bot_line = tk.Frame(card, bg="#0d1117")
            bot_line.pack(fill="x", pady=(8, 0))

            lbl_cal = tk.Label(bot_line, image=self.img_cal, bg="#0d1117")
            lbl_cal.pack(side="left", padx=(0, 4))

            lbl_date = tk.Label(
                bot_line,
                text=att["date"],
                font=("Segoe UI", 9),
                fg="#9ca3af",
                bg="#0d1117"
            )
            lbl_date.pack(side="left", padx=(0, 16))

            lbl_wr = tk.Label(bot_line, image=self.img_wrench, bg="#0d1117")
            lbl_wr.pack(side="left", padx=(0, 4))

            lbl_veh = tk.Label(
                bot_line,
                text=att["vehicle"],
                font=("Segoe UI", 9),
                fg="#9ca3af",
                bg="#0d1117"
            )
            lbl_veh.pack(side="left")

            btn_view = tk.Button(
                bot_line,
                text=" Abrir PDF",
                image=self.img_eye,
                compound="left",
                font=("Segoe UI", 9, "bold"),
                fg="#60a5fa",
                bg="#0d1117",
                activebackground="#1c2538",
                bd=0,
                cursor="hand2",
                command=lambda url=att["pdf_url"], a=att: self._open_pdf(url, a)
            )
            btn_view.pack(side="right")

    def _open_pdf(self, url: str, att: dict):
        final_data = {
            "client": {"nome": "Logística TransBrasil Ltda", "cpf_cnpj": "12.345.678/0001-90", "cidade": "São Paulo", "uf": "SP"},
            "tecnico": "Carlos Eduardo - Mecânico Chefe",
            "observacoes": "Alinhamento e geometria dos eixos realizados conforme especificações de fábrica.",
            "units": [
                {"type": "Cavalo Mecânico", "model": att.get("vehicle", "VOLVO FH 540"), "placa": "ABC1D23", "km": "245000"}
            ]
        }

        filename = f"Relatorio_Alinhamento_OS_{att['id']}.pdf"

        try:
            pdf_path = generate_alignment_pdf(final_data, filename=filename)
            messagebox.showinfo(
                "Abrindo Relatório PDF",
                f"Abrindo relatório PDF salvo do Atendimento #{att['id']}:\n\n"
                f"Veículo: {att['vehicle']}\nData: {att['date']}\n\n"
                f"Arquivo: {pdf_path}"
            )
            webbrowser.open(f"file://{pdf_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir PDF", f"Não foi possível abrir o PDF do atendimento: {e}")
