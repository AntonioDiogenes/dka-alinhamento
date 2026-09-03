"""
Tela de Gestão e Listagem de Clientes (views/clientes/index.py).
Reconstrução fiel da especificação visual da versão Desktop:
- Estética Dark Theme Técnico / Pátio de Oficina (#111520, #1a1f2e, #0d1117, #161b26).
- AlignmentHeader com botão "+ Novo Cliente".
- Tabela com colunas estritamente alinhadas (uniform grid column configuration).
- Ações no perfil (Visualizar, Editar, Excluir).
- Rodapé com paginação integrada e mensagem de estado vazio.
"""
import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any

from app.config.settings import COLORS, FONTS
from app.services.client_service import ClientService
from app.utils.icons import create_icon_image

class ClientesIndexView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.router = router

        # Estado da View e Paginação
        self.all_clients: List[Dict[str, Any]] = ClientService.get_all_clients()
        self.filtered_clients: List[Dict[str, Any]] = list(self.all_clients)
        self.page_size = 7
        self.current_page = 1

        # Ícones
        self.img_back = create_icon_image("arrow_left", size=20, color="#FFFFFF")
        self.img_plus = create_icon_image("plus", size=18, color="#FFFFFF")
        self.img_user = create_icon_image("user", size=16, color="#8a94a6")
        self.img_file = create_icon_image("file_text", size=16, color="#8a94a6")
        self.img_pin = create_icon_image("map_pin", size=16, color="#8a94a6")
        self.img_truck = create_icon_image("truck", size=16, color="#8a94a6")
        self.img_eye = create_icon_image("eye", size=18, color="#60a5fa")
        self.img_pencil = create_icon_image("pencil", size=18, color="#f59e0b")
        self.img_trash = create_icon_image("trash", size=18, color="#ef4444")
        self.img_prev = create_icon_image("chevron_left", size=18, color="#FFFFFF")
        self.img_next = create_icon_image("chevron_right", size=18, color="#FFFFFF")

        self._build_ui()
        self._apply_filters()

    def _build_ui(self):
        # ------------------------------------------
        # 1. AlignmentHeader (Topo)
        # ------------------------------------------
        self.header = tk.Frame(
            self,
            bg=COLORS["bg_dark"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=28,
            pady=16
        )
        self.header.pack(fill="x", side="top")

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

        self.lbl_title = tk.Label(
            self.header,
            text="Clientes",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_dark"]
        )
        self.lbl_title.pack(side="left")

        self.btn_create = tk.Button(
            self.header,
            text=" + Novo Cliente ",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self.router.navigate("clientes.create")
        )
        self.btn_create.pack(side="right")

        # ------------------------------------------
        # 2. Toolbar Superior (#1a1f2e)
        # ------------------------------------------
        self.toolbar = tk.Frame(
            self,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=28,
            pady=14
        )
        self.toolbar.pack(fill="x", side="top")

        self.var_filter_placa = tk.StringVar()

        self.btn_clear_filters = tk.Button(
            self.toolbar,
            text=" Limpar Filtros",
            font=("Segoe UI", 10, "bold"),
            fg="#f87171",
            bg="#2a1820",
            activebackground="#3d1d28",
            bd=1,
            highlightbackground="#ef4444",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._clear_filters
        )
        self.btn_clear_filters.pack(side="left")

        # Campo de busca por Placa na Toolbar
        placa_box = tk.Frame(
            self.toolbar,
            bg="#0d1117",
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=10,
            pady=4
        )
        placa_box.pack(side="left", padx=(16, 0))

        lbl_p_icon = tk.Label(placa_box, image=self.img_truck, bg="#0d1117")
        lbl_p_icon.pack(side="left", padx=(0, 6))

        entry_p = tk.Entry(
            placa_box,
            textvariable=self.var_filter_placa,
            bg="#0d1117",
            fg=COLORS["text_white"],
            insertbackground="white",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 11)
        )
        entry_p.pack(side="left", fill="x", ipady=4)

        def on_p_focus_in(e):
            if entry_p.get() == "Filtrar placa...":
                entry_p.delete(0, tk.END)
                entry_p.config(fg=COLORS["text_white"])

        def on_p_focus_out(e):
            if not entry_p.get():
                entry_p.insert(0, "Filtrar placa...")
                entry_p.config(fg="#6b7280")

        entry_p.insert(0, "Filtrar placa...")
        entry_p.config(fg="#6b7280")
        entry_p.bind("<FocusIn>", on_p_focus_in)
        entry_p.bind("<FocusOut>", on_p_focus_out)
        entry_p.bind("<KeyRelease>", lambda e: self._on_filter_changed())

        # ------------------------------------------
        # 3. Card Envelopador da Tabela (#1a1f2e)
        # ------------------------------------------
        self.main_area = tk.Frame(self, bg=COLORS["bg_dark"], padx=28, pady=20)
        self.main_area.pack(fill="both", expand=True)

        self.table_card = tk.Frame(
            self.main_area,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1
        )
        self.table_card.pack(fill="both", expand=True)

        self.table_card.grid_rowconfigure(0, weight=0) # Títulos
        self.table_card.grid_rowconfigure(1, weight=0) # Filtros
        self.table_card.grid_rowconfigure(2, weight=1) # Dados
        self.table_card.grid_rowconfigure(3, weight=0) # Rodapé
        self.table_card.grid_columnconfigure(0, weight=1)

        # ------------------------------------------
        # 3A. LINHA 1 — TÍTULOS DA TABELA (#0d1117)
        # ------------------------------------------
        self.titles_row = tk.Frame(self.table_card, bg="#0d1117", padx=16, pady=12)
        self.titles_row.grid(row=0, column=0, sticky="ew")

        # Configuração UNIFORME estrita das colunas para alinhamento 100% reto
        self.titles_row.grid_columnconfigure(0, weight=2, uniform="cli_col")
        self.titles_row.grid_columnconfigure(1, weight=3, uniform="cli_col")
        self.titles_row.grid_columnconfigure(2, weight=3, uniform="cli_col")
        self.titles_row.grid_columnconfigure(3, weight=2, uniform="cli_col")
        self.titles_row.grid_columnconfigure(4, weight=2, uniform="cli_col")

        cols = ["Data de Cadastro", "Nome", "CPF/CNPJ", "Cidade", "Ações"]
        for idx, col_name in enumerate(cols):
            lbl = tk.Label(
                self.titles_row,
                text=col_name,
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["text_white"],
                bg="#0d1117",
                anchor="e" if col_name == "Ações" else "w"
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=12)

        # ------------------------------------------
        # 3B. LINHA 2 — INPUTS DE FILTRO (#161b26)
        # ------------------------------------------
        self.filters_row = tk.Frame(
            self.table_card,
            bg="#161b26",
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
            padx=16,
            pady=8
        )
        self.filters_row.grid(row=1, column=0, sticky="ew")

        self.filters_row.grid_columnconfigure(0, weight=2, uniform="cli_col")
        self.filters_row.grid_columnconfigure(1, weight=3, uniform="cli_col")
        self.filters_row.grid_columnconfigure(2, weight=3, uniform="cli_col")
        self.filters_row.grid_columnconfigure(3, weight=2, uniform="cli_col")
        self.filters_row.grid_columnconfigure(4, weight=2, uniform="cli_col")

        self.var_filter_nome = tk.StringVar()
        self.var_filter_cpf = tk.StringVar()
        self.var_filter_cidade = tk.StringVar()

        tk.Label(self.filters_row, bg="#161b26").grid(row=0, column=0, sticky="ew", padx=12)
        self._create_filter_input(self.filters_row, self.img_user, self.var_filter_nome, "Filtrar nome...", col=1)
        self._create_filter_input(self.filters_row, self.img_file, self.var_filter_cpf, "Filtrar CPF/CNPJ...", col=2)
        self._create_filter_input(self.filters_row, self.img_pin, self.var_filter_cidade, "Filtrar cidade...", col=3)
        tk.Label(self.filters_row, bg="#161b26").grid(row=0, column=4, sticky="ew", padx=12)

        # ------------------------------------------
        # 3C. LINHAS DE DADOS (Scroll Container)
        # ------------------------------------------
        self.rows_container = tk.Frame(self.table_card, bg=COLORS["bg_card"])
        self.rows_container.grid(row=2, column=0, sticky="nsew")

        # ------------------------------------------
        # 3D. RODAPÉ DE PAGINAÇÃO
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
            padx=10,
            pady=6
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
            font=("Segoe UI", 11)
        )
        entry.pack(side="left", fill="x", expand=True, ipady=4)

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
        n_val = self.var_filter_nome.get()
        c_val = self.var_filter_cpf.get()
        cid_val = self.var_filter_cidade.get()
        p_val = self.var_filter_placa.get()

        n_f = "" if n_val == "Filtrar nome..." else n_val
        c_f = "" if c_val == "Filtrar CPF/CNPJ..." else c_val
        cid_f = "" if cid_val == "Filtrar cidade..." else cid_val
        p_f = "" if p_val == "Filtrar placa..." else p_val

        self.filtered_clients = ClientService.filter_clients(
            nome_filter=n_f,
            cpf_cnpj_filter=c_f,
            cidade_filter=cid_f,
            placa_filter=p_f
        )
        self._render_rows()

    def _clear_filters(self):
        self.var_filter_nome.set("")
        self.var_filter_cpf.set("")
        self.var_filter_cidade.set("")
        self.var_filter_placa.set("")
        self.current_page = 1
        self._apply_filters()

    def _render_rows(self):
        for child in self.rows_container.winfo_children():
            child.destroy()

        total = len(self.filtered_clients)
        card_bg = COLORS["bg_card"]

        if total == 0:
            empty_frame = tk.Frame(self.rows_container, bg=card_bg, pady=48)
            empty_frame.pack(fill="both", expand=True)

            lbl_empty = tk.Label(empty_frame, text="Nenhum cliente encontrado.", font=("Segoe UI", 11), fg="#9ca3af", bg=card_bg)
            lbl_empty.pack(expand=True)
            self._update_pagination_info(0, 0, 0)
            return

        total_pages = math.ceil(total / self.page_size) or 1
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total)
        page_items = self.filtered_clients[start_idx:end_idx]

        for item in page_items:
            row_frame = tk.Frame(
                self.rows_container,
                bg=card_bg,
                highlightbackground=COLORS["border_subtle"],
                highlightthickness=1,
                cursor="hand2",
                padx=16,
                pady=12
            )
            row_frame.pack(fill="x", side="top")

            # Configuração UNIFORME estrita das colunas para alinhamento 100% reto
            row_frame.grid_columnconfigure(0, weight=2, uniform="cli_col")
            row_frame.grid_columnconfigure(1, weight=3, uniform="cli_col")
            row_frame.grid_columnconfigure(2, weight=3, uniform="cli_col")
            row_frame.grid_columnconfigure(3, weight=2, uniform="cli_col")
            row_frame.grid_columnconfigure(4, weight=2, uniform="cli_col")

            def on_enter(e, f=row_frame):
                f.configure(bg="#22293a")
                for w in f.winfo_children():
                    if isinstance(w, tk.Label):
                        w.configure(bg="#22293a")

            def on_leave(e, f=row_frame):
                f.configure(bg=card_bg)
                for w in f.winfo_children():
                    if isinstance(w, tk.Label):
                        w.configure(bg=card_bg)

            def on_click(e, c=item):
                self.router.navigate("clientes.show", client_id=c["id"])

            row_frame.bind("<Enter>", on_enter)
            row_frame.bind("<Leave>", on_leave)
            row_frame.bind("<Button-1>", on_click)

            # 1. Data de Cadastro / Serviço
            lbl_date = tk.Label(row_frame, text=item.get("date_service", "17/08/2026"), font=("Segoe UI", 10), fg="#64748b", bg=card_bg, anchor="w")
            lbl_date.grid(row=0, column=0, sticky="ew", padx=12)
            lbl_date.bind("<Button-1>", on_click)

            # 2. Nome
            lbl_name = tk.Label(row_frame, text=item["nome"], font=("Segoe UI", 10, "bold"), fg=COLORS["text_white"], bg=card_bg, anchor="w")
            lbl_name.grid(row=0, column=1, sticky="ew", padx=12)
            lbl_name.bind("<Button-1>", on_click)

            # 3. CPF/CNPJ
            lbl_cpf = tk.Label(
                row_frame,
                text=item["cpf_cnpj"],
                font=("Consolas", 10),
                fg="#9ca3af",
                bg=card_bg,
                anchor="w"
            )
            lbl_cpf.grid(row=0, column=2, sticky="ew", padx=12)
            lbl_cpf.bind("<Button-1>", on_click)

            # 4. Cidade
            lbl_cidade = tk.Label(row_frame, text=f"{item['cidade']} - {item['uf']}", font=("Segoe UI", 10), fg="#d1d5db", bg=card_bg, anchor="w")
            lbl_cidade.grid(row=0, column=3, sticky="ew", padx=12)
            lbl_cidade.bind("<Button-1>", on_click)

            # 5. Coluna de Ações (Visualizar, Editar, Excluir)
            act_frame = tk.Frame(row_frame, bg=card_bg)
            act_frame.grid(row=0, column=4, sticky="e", padx=12)

            btn_v = tk.Button(act_frame, image=self.img_eye, bg=card_bg, activebackground="#22293a", bd=0, cursor="hand2", command=lambda c=item: self.router.navigate("clientes.show", client_id=c["id"]))
            btn_v.pack(side="left", padx=4)

            btn_e = tk.Button(act_frame, image=self.img_pencil, bg=card_bg, activebackground="#22293a", bd=0, cursor="hand2", command=lambda c=item: self.router.navigate("clientes.edit", client_id=c["id"]))
            btn_e.pack(side="left", padx=4)

            btn_d = tk.Button(act_frame, image=self.img_trash, bg=card_bg, activebackground="#22293a", bd=0, cursor="hand2", command=lambda c=item: self._delete_client(c["id"]))
            btn_d.pack(side="left", padx=4)

        self._update_pagination_info(start_idx + 1, end_idx, total)

    def _update_pagination_info(self, start: int, end: int, total: int):
        if total == 0:
            self.lbl_page_info.config(text="Exibindo 0 clientes")
            self.lbl_page_num.config(text="Página 0 de 0")
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            total_pages = math.ceil(total / self.page_size)
            self.lbl_page_info.config(text=f"Exibindo {start} a {end} de {total} clientes")
            self.lbl_page_num.config(text=f"Página {self.current_page} de {total_pages}")
            
            self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
            self.btn_next.config(state="normal" if self.current_page < total_pages else "disabled")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_rows()

    def _next_page(self):
        total_pages = math.ceil(len(self.filtered_clients) / self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_rows()

    def _delete_client(self, client_id: int):
        if messagebox.askyesno("Excluir Cliente", "Tem certeza que deseja remover este cliente?"):
            ClientService.delete_client(client_id)
            self.all_clients = ClientService.get_all_clients()
            self._apply_filters()
