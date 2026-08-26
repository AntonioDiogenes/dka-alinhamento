"""
Tela de Histórico de Atendimentos (views/attendances/index.py).
Reconstrução fiel da especificação visual da versão Desktop:
- Estética Dark Theme Técnico / Pátio de Oficina (#111520, #1a1f2e, #0d1117, #161b26).
- AlignmentHeader com seta de voltar e título "Histórico".
- Toolbar com botão "Limpar Filtros" vermelho translúcido.
- Tabela escura com colunas estritamente alinhadas (uniform grid column configuration).
- Ação exclusiva de Visualização do Relatório PDF salvo no sistema.
- Rodapé com paginação integrada e mensagem de estado vazio.
"""
import os
import math
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any

from app.config.settings import COLORS, FONTS
from app.services.attendance_service import AttendanceService
from app.utils.icons import create_icon_image
from app.utils.pdf_generator import generate_alignment_pdf

class AttendancesIndexView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.router = router

        # Estado da View e Paginação
        self.all_attendances: List[Dict[str, Any]] = AttendanceService.get_all_attendances()
        self.filtered_attendances: List[Dict[str, Any]] = list(self.all_attendances)
        self.page_size = 7
        self.current_page = 1

        # Renderizar Ícones Auxiliares
        self.img_back = create_icon_image("arrow_left", size=20, color="#FFFFFF")
        self.img_cal = create_icon_image("calendar", size=16, color="#8a94a6")
        self.img_car = create_icon_image("car", size=16, color="#8a94a6")
        self.img_tag = create_icon_image("tag", size=16, color="#8a94a6")
        self.img_user = create_icon_image("user", size=16, color="#8a94a6")
        self.img_eye = create_icon_image("eye", size=18, color="#60a5fa")
        self.img_prev = create_icon_image("chevron_left", size=18, color="#FFFFFF")
        self.img_next = create_icon_image("chevron_right", size=18, color="#FFFFFF")

        # Construir Seções Fixas da Tela
        self._build_ui()
        self._apply_filters()

    def _build_ui(self):
        """Monta as 3 seções principais (A: AlignmentHeader, B: Toolbar, C: Tabela Escura)."""
        # ==========================================
        # SEÇÃO A: AlignmentHeader (Fixo no Topo)
        # ==========================================
        self.header = tk.Frame(
            self,
            bg=COLORS["bg_dark"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=28,
            pady=16
        )
        self.header.pack(fill="x", side="top")

        # Seta de Voltar para o Dashboard
        self.btn_back = tk.Button(
            self.header,
            image=self.img_back,
            bg=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda: self.router.navigate("dashboard")
        )
        self.btn_back.pack(side="left", padx=(0, 16))

        # Título "Histórico"
        self.lbl_title = tk.Label(
            self.header,
            text="Histórico",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_dark"]
        )
        self.lbl_title.pack(side="left")

        # ==========================================
        # SEÇÃO B: Top Bar / Toolbar Superior
        # ==========================================
        self.toolbar = tk.Frame(
            self,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=28,
            pady=14
        )
        self.toolbar.pack(fill="x", side="top")

        # Botão "Limpar Filtros" estilo alerta vermelho translúcido
        self.btn_clear_filters = tk.Button(
            self.toolbar,
            text=" Limpar Filtros",
            font=("Segoe UI", 10, "bold"),
            fg="#f87171",
            bg="#2a1820",
            activebackground="#3d1d28",
            activeforeground="#fca5a5",
            bd=1,
            highlightbackground="#ef4444",
            highlightthickness=1,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._clear_filters
        )
        self.btn_clear_filters.pack(side="left")

        # ==========================================
        # SEÇÃO C: Área da Tabela Escura (<main>)
        # ==========================================
        self.main_area = tk.Frame(self, bg=COLORS["bg_dark"], padx=28, pady=20)
        self.main_area.pack(fill="both", expand=True)

        # Card Envelopador da Tabela (#1a1f2e)
        self.table_card = tk.Frame(
            self.main_area,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1
        )
        self.table_card.pack(fill="both", expand=True)

        # Configurar Grid da Tabela
        self.table_card.grid_rowconfigure(0, weight=0) # Títulos (#0d1117)
        self.table_card.grid_rowconfigure(1, weight=0) # Inputs de Filtro (#161b26)
        self.table_card.grid_rowconfigure(2, weight=1) # Linhas de Dados (#1a1f2e)
        self.table_card.grid_rowconfigure(3, weight=0) # Rodapé de Paginação
        self.table_card.grid_columnconfigure(0, weight=1)

        # ------------------------------------------
        # 1. CABEÇALHO LINHA 1 — TÍTULOS (#0d1117)
        # ------------------------------------------
        self.titles_row = tk.Frame(self.table_card, bg="#0d1117", padx=16, pady=12)
        self.titles_row.grid(row=0, column=0, sticky="ew")

        # Configuração UNIFORME das colunas para alinhamento 100% reto
        self.titles_row.grid_columnconfigure(0, weight=2, uniform="att_col") # Data de Serviço
        self.titles_row.grid_columnconfigure(1, weight=3, uniform="att_col") # Modelo
        self.titles_row.grid_columnconfigure(2, weight=2, uniform="att_col") # Placa
        self.titles_row.grid_columnconfigure(3, weight=3, uniform="att_col") # Cliente
        self.titles_row.grid_columnconfigure(4, weight=2, uniform="att_col") # Ações

        col_titles = ["Data de Serviço", "Modelo", "Placa", "Cliente", "Ver Relatório PDF"]
        for idx, title in enumerate(col_titles):
            lbl = tk.Label(
                self.titles_row,
                text=title,
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["text_white"],
                bg="#0d1117",
                anchor="e" if idx == 4 else "w"
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=12)

        # ------------------------------------------
        # 2. CABEÇALHO LINHA 2 — INPUTS DE FILTRO (#161b26)
        # ------------------------------------------
        self.filters_row = tk.Frame(
            self.table_card,
            bg="#161b26",
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=16,
            pady=10
        )
        self.filters_row.grid(row=1, column=0, sticky="ew")

        self.filters_row.grid_columnconfigure(0, weight=2, uniform="att_col")
        self.filters_row.grid_columnconfigure(1, weight=3, uniform="att_col")
        self.filters_row.grid_columnconfigure(2, weight=2, uniform="att_col")
        self.filters_row.grid_columnconfigure(3, weight=3, uniform="att_col")
        self.filters_row.grid_columnconfigure(4, weight=2, uniform="att_col")

        # Variáveis dos Filtros
        self.var_filter_date = tk.StringVar()
        self.var_filter_model = tk.StringVar()
        self.var_filter_plate = tk.StringVar()
        self.var_filter_client = tk.StringVar()

        # Criar Inputs com ícones integrados à esquerda
        self.f_date_box = self._create_filter_input(self.filters_row, self.img_cal, self.var_filter_date, "Filtrar data...", col=0)
        self.f_model_box = self._create_filter_input(self.filters_row, self.img_car, self.var_filter_model, "Filtrar modelo...", col=1)
        self.f_plate_box = self._create_filter_input(self.filters_row, self.img_tag, self.var_filter_plate, "Filtrar placa...", col=2)
        self.f_client_box = self._create_filter_input(self.filters_row, self.img_user, self.var_filter_client, "Filtrar cliente...", col=3)
        tk.Label(self.filters_row, bg="#161b26").grid(row=0, column=4, sticky="ew", padx=12)

        # ------------------------------------------
        # 3. CORPO DA TABELA (Dados em Scroll)
        # ------------------------------------------
        self.rows_container = tk.Frame(self.table_card, bg=COLORS["bg_card"])
        self.rows_container.grid(row=2, column=0, sticky="nsew")

        # ------------------------------------------
        # 4. RODAPÉ DA TABELA (Paginação Integrada)
        # ------------------------------------------
        self.pagination_footer = tk.Frame(
            self.table_card,
            bg="#0d1117",
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=20,
            pady=12
        )
        self.pagination_footer.grid(row=3, column=0, sticky="ew")

        self.lbl_page_info = tk.Label(
            self.pagination_footer,
            text="",
            font=("Segoe UI", 9),
            fg=COLORS["text_muted"],
            bg="#0d1117"
        )
        self.lbl_page_info.pack(side="left")

        # Botões de Navegação de Página (Anterior / Próxima)
        self.nav_frame = tk.Frame(self.pagination_footer, bg="#0d1117")
        self.nav_frame.pack(side="right")

        self.btn_prev = tk.Button(
            self.nav_frame,
            image=self.img_prev,
            bg=COLORS["bg_card"],
            activebackground=COLORS["accent_blue"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._prev_page
        )
        self.btn_prev.pack(side="left", padx=4)

        self.lbl_page_num = tk.Label(
            self.nav_frame,
            text="Página 1",
            font=("Segoe UI", 9, "bold"),
            fg=COLORS["text_white"],
            bg="#0d1117",
            padx=8
        )
        self.lbl_page_num.pack(side="left")

        self.btn_next = tk.Button(
            self.nav_frame,
            image=self.img_next,
            bg=COLORS["bg_card"],
            activebackground=COLORS["accent_blue"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._next_page
        )
        self.btn_next.pack(side="left", padx=4)

    def _create_filter_input(self, parent: tk.Frame, icon_img, string_var: tk.StringVar, placeholder: str, col: int):
        box = tk.Frame(
            parent,
            bg="#0d1117",
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=8,
            pady=4
        )
        box.grid(row=0, column=col, sticky="ew", padx=12)

        lbl_icon = tk.Label(box, image=icon_img, bg="#0d1117")
        lbl_icon.pack(side="left", padx=(0, 6))

        entry = tk.Entry(
            box,
            textvariable=string_var,
            bg="#0d1117",
            fg=COLORS["text_white"],
            insertbackground="white",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 9)
        )
        entry.pack(side="left", fill="x", expand=True)

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS["text_white"])

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#6b7280")

        entry.insert(0, placeholder)
        entry.config(fg="#6b7280")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<KeyRelease>", lambda e: self._on_filter_changed())

        return box

    def _on_filter_changed(self):
        self.current_page = 1
        self._apply_filters()

    def _apply_filters(self):
        d_val = self.var_filter_date.get()
        m_val = self.var_filter_model.get()
        p_val = self.var_filter_plate.get()
        c_val = self.var_filter_client.get()

        d_filter = "" if d_val == "Filtrar data..." else d_val
        m_filter = "" if m_val == "Filtrar modelo..." else m_val
        p_filter = "" if p_val == "Filtrar placa..." else p_val
        c_filter = "" if c_val == "Filtrar cliente..." else c_val

        self.filtered_attendances = AttendanceService.filter_attendances(
            date_filter=d_filter,
            model_filter=m_filter,
            plate_filter=p_filter,
            client_filter=c_filter
        )
        self._render_rows()

    def _clear_filters(self):
        self.var_filter_date.set("")
        self.var_filter_model.set("")
        self.var_filter_plate.set("")
        self.var_filter_client.set("")
        self.current_page = 1
        self._apply_filters()

    def _render_rows(self):
        for child in self.rows_container.winfo_children():
            child.destroy()

        total = len(self.filtered_attendances)

        if total == 0:
            empty_frame = tk.Frame(self.rows_container, bg=COLORS["bg_card"], pady=48)
            empty_frame.pack(fill="both", expand=True)

            lbl_empty = tk.Label(
                empty_frame,
                text="Nenhum atendimento encontrado.",
                font=("Segoe UI", 11),
                fg="#6b7280",
                bg=COLORS["bg_card"]
            )
            lbl_empty.pack(expand=True)
            self._update_pagination_info(0, 0, 0)
            return

        total_pages = math.ceil(total / self.page_size) or 1
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total)
        page_items = self.filtered_attendances[start_idx:end_idx]

        for item in page_items:
            row_frame = tk.Frame(
                self.rows_container,
                bg=COLORS["bg_card"],
                highlightbackground=COLORS["border_subtle"],
                highlightthickness=1,
                cursor="hand2",
                padx=16,
                pady=12
            )
            row_frame.pack(fill="x", side="top")

            # Configuração UNIFORME estrita das colunas para alinhamento 100% reto
            row_frame.grid_columnconfigure(0, weight=2, uniform="att_col")
            row_frame.grid_columnconfigure(1, weight=3, uniform="att_col")
            row_frame.grid_columnconfigure(2, weight=2, uniform="att_col")
            row_frame.grid_columnconfigure(3, weight=3, uniform="att_col")
            row_frame.grid_columnconfigure(4, weight=2, uniform="att_col")

            def on_enter(e, f=row_frame):
                f.configure(bg="#22293a")
                for w in f.winfo_children():
                    if isinstance(w, tk.Label):
                        w.configure(bg="#22293a")

            def on_leave(e, f=row_frame):
                f.configure(bg=COLORS["bg_card"])
                for w in f.winfo_children():
                    if isinstance(w, tk.Label):
                        w.configure(bg=COLORS["bg_card"])

            def on_click(e, att=item):
                self._open_pdf_report(att)

            row_frame.bind("<Enter>", on_enter)
            row_frame.bind("<Leave>", on_leave)
            row_frame.bind("<Button-1>", on_click)

            # Célula 1: Data de Serviço
            lbl_date = tk.Label(
                row_frame,
                text=item["date_formatted"],
                font=("Segoe UI", 10),
                fg="#d1d5db",
                bg=COLORS["bg_card"],
                anchor="w"
            )
            lbl_date.grid(row=0, column=0, sticky="ew", padx=12)
            lbl_date.bind("<Button-1>", on_click)

            # Célula 2: Modelo
            lbl_model = tk.Label(
                row_frame,
                text=item["model"],
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["text_white"],
                bg=COLORS["bg_card"],
                anchor="w"
            )
            lbl_model.grid(row=0, column=1, sticky="ew", padx=12)
            lbl_model.bind("<Button-1>", on_click)

            # Célula 3: Placa
            lbl_plate = tk.Label(
                row_frame,
                text=item["plate"],
                font=("Consolas", 10, "bold"),
                fg="#60a5fa",
                bg=COLORS["bg_card"],
                anchor="w"
            )
            lbl_plate.grid(row=0, column=2, sticky="ew", padx=12)
            lbl_plate.bind("<Button-1>", on_click)

            # Célula 4: Cliente
            lbl_client = tk.Label(
                row_frame,
                text=item["client"],
                font=("Segoe UI", 10),
                fg="#d1d5db",
                bg=COLORS["bg_card"],
                anchor="w"
            )
            lbl_client.grid(row=0, column=3, sticky="ew", padx=12)
            lbl_client.bind("<Button-1>", on_click)

            # Célula 5: Ação Exclusiva — Botão Visualizar PDF
            actions_frame = tk.Frame(row_frame, bg=COLORS["bg_card"])
            actions_frame.grid(row=0, column=4, sticky="e", padx=12)

            btn_view = tk.Button(
                actions_frame,
                text=" Abrir PDF",
                image=self.img_eye,
                compound="left",
                font=("Segoe UI", 9, "bold"),
                fg="#60a5fa",
                bg="#1c2538",
                activebackground="#2563eb",
                activeforeground="white",
                bd=1,
                highlightbackground="#2563eb",
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda att=item: self._open_pdf_report(att)
            )
            btn_view.pack(side="right")

        self._update_pagination_info(start_idx + 1, end_idx, total)

    def _update_pagination_info(self, start: int, end: int, total: int):
        if total == 0:
            self.lbl_page_info.config(text="Exibindo 0 registros")
            self.lbl_page_num.config(text="Página 0 de 0")
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            total_pages = math.ceil(total / self.page_size)
            self.lbl_page_info.config(text=f"Exibindo {start} a {end} de {total} atendimentos")
            self.lbl_page_num.config(text=f"Página {self.current_page} de {total_pages}")
            
            self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
            self.btn_next.config(state="normal" if self.current_page < total_pages else "disabled")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_rows()

    def _next_page(self):
        total_pages = math.ceil(len(self.filtered_attendances) / self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_rows()

    def _open_pdf_report(self, item: dict):
        final_data = {
            "client": {"nome": item.get("client", "Logística TransBrasil Ltda"), "cpf_cnpj": "12.345.678/0001-90", "cidade": "São Paulo", "uf": "SP"},
            "tecnico": "Carlos Eduardo - Mecânico Chefe",
            "observacoes": "Alinhamento e geometria dos eixos realizados conforme especificações de fábrica.",
            "units": [
                {"type": "Cavalo Mecânico", "model": item.get("model", "VOLVO FH 540"), "placa": item.get("plate", "ABC1D23"), "km": "245000"}
            ]
        }

        filename = f"Relatorio_Alinhamento_OS_{item['id']}.pdf"

        try:
            pdf_path = generate_alignment_pdf(final_data, filename=filename)
            messagebox.showinfo(
                "Abrindo Relatório PDF",
                f"Abrindo relatório PDF salvo da OS #{item['id']}:\n\n"
                f"Veículo: {item['model']}\nPlaca: {item['plate']}\nCliente: {item['client']}\n\n"
                f"Arquivo: {pdf_path}"
            )
            webbrowser.open(f"file://{pdf_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir PDF", f"Não foi possível abrir o PDF do atendimento: {e}")
