"""
Tela de Gerenciamento e CRUD de Mecânicos / Técnicos (views/configuracoes/mecanicos.py).
Permite visualizar, buscar, criar, editar e excluir mecânicos e técnicos da oficina.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any, Optional

from app.config.settings import COLORS, FONTS
from app.services.mechanic_service import MechanicService
from app.components.alignment_header import AlignmentHeader
from app.utils.icons import create_icon_image
from app.utils.scroll_helper import setup_canvas_scrolling

ESPECIALIDADES_LISTA = [
    "Mecânico Chefe",
    "Técnico Alinhador",
    "Especialista em Geometria",
    "Técnico de Suspensão",
    "Auxiliar Técnico",
    "Mecânico Geral"
]

class MecanicosView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router

        self.all_mechanics: List[Dict[str, Any]] = []
        self.filtered_mechanics: List[Dict[str, Any]] = []

        # Ícones
        self.img_search = create_icon_image("search", size=16, color="#8a94a6")
        self.img_clear = create_icon_image("x", size=14, color="#8a94a6")
        self.img_plus = create_icon_image("plus", size=16, color="#FFFFFF")
        self.img_pencil = create_icon_image("pencil", size=16, color="#f59e0b")
        self.img_trash = create_icon_image("trash", size=16, color="#ef4444")

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # 1. CABEÇALHO TÉCNICO
        self.header = AlignmentHeader(
            self,
            title="Configurações",
            subtitle="Mecânicos e Técnicos da Oficina",
            on_back=lambda: self.router.navigate("dashboard"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # 2. BARRA DE FERRAMENTAS E BUSCA
        self.toolbar_container = tk.Frame(self, bg="#111520", padx=32, pady=16)
        self.toolbar_container.pack(fill="x", side="top")

        self.toolbar = tk.Frame(self.toolbar_container, bg="#111520")
        self.toolbar.pack(fill="x")

        # Campo de Busca (#0d1117)
        self.search_box = tk.Frame(
            self.toolbar,
            bg="#0d1117",
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=10,
            pady=6
        )
        self.search_box.pack(side="left", fill="x", expand=True, padx=(0, 16))

        lbl_search_icon = tk.Label(self.search_box, image=self.img_search, bg="#0d1117")
        lbl_search_icon.pack(side="left", padx=(0, 8))

        self.entry_search = tk.Entry(
            self.search_box,
            bg="#0d1117",
            fg="#FFFFFF",
            insertbackground="white",
            bd=0,
            font=("Segoe UI", 11)
        )
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=4)

        self.entry_search.insert(0, "Buscar por nome, especialidade ou celular...")
        self.entry_search.config(fg="#8a94a6")

        def on_focus_in(e):
            if self.entry_search.get() == "Buscar por nome, especialidade ou celular...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg="#FFFFFF")

        def on_focus_out(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Buscar por nome, especialidade ou celular...")
                self.entry_search.config(fg="#8a94a6")

        self.entry_search.bind("<FocusIn>", on_focus_in)
        self.entry_search.bind("<FocusOut>", on_focus_out)
        self.entry_search.bind("<KeyRelease>", lambda e: self._apply_filter())

        self.btn_clear = tk.Button(
            self.search_box,
            image=self.img_clear,
            bg="#0d1117",
            activebackground="#1c2230",
            bd=0,
            cursor="hand2",
            command=self._clear_search
        )
        self.btn_clear.pack(side="right")

        # Botão + Novo Mecânico
        self.btn_add = tk.Button(
            self.toolbar,
            text=" + Novo Mecânico ",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#10b981",
            activebackground="#059669",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._open_create_modal
        )
        self.btn_add.pack(side="right")

        # 3. CONTAINER DA TABELA DE MECÂNICOS
        self.table_card = tk.Frame(self, bg="#1a1f2e", highlightbackground="#2a3245", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        # Cabeçalho da Tabela
        self.th_frame = tk.Frame(self.table_card, bg="#111520", padx=16, pady=10)
        self.th_frame.pack(fill="x", side="top")

        self.th_frame.grid_columnconfigure(0, weight=1, uniform="mec_col") # ID
        self.th_frame.grid_columnconfigure(1, weight=4, uniform="mec_col") # NOME
        self.th_frame.grid_columnconfigure(2, weight=3, uniform="mec_col") # ESPECIALIDADE
        self.th_frame.grid_columnconfigure(3, weight=3, uniform="mec_col") # CELULAR
        self.th_frame.grid_columnconfigure(4, weight=2, uniform="mec_col") # STATUS
        self.th_frame.grid_columnconfigure(5, weight=2, uniform="mec_col") # AÇÕES

        tk.Label(self.th_frame, text="ID", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(self.th_frame, text="NOME DO MECÂNICO / TÉCNICO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(self.th_frame, text="ESPECIALIDADE / CARGO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(self.th_frame, text="CELULAR / TELEFONE", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(self.th_frame, text="STATUS", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=4, sticky="ew")
        tk.Label(self.th_frame, text="AÇÕES", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="e").grid(row=0, column=5, sticky="ew")

        # Área de Rolagem com Canvas
        self.list_canvas = tk.Canvas(self.table_card, bg="#1a1f2e", highlightthickness=0, bd=0)
        self.list_canvas.pack(fill="both", expand=True, side="top")

        self.list_inner = tk.Frame(self.list_canvas, bg="#1a1f2e")
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")

        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(self.list_window, width=e.width))
        self.list_inner.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        setup_canvas_scrolling(self.list_canvas, self.list_inner)

    def _load_data(self):
        self.all_mechanics = MechanicService.get_all_mechanics()
        self._apply_filter()

    def _clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, "Buscar por nome, especialidade ou celular...")
        self.entry_search.config(fg="#8a94a6")
        self._apply_filter()

    def _apply_filter(self):
        q = self.entry_search.get().strip()
        if q == "Buscar por nome, especialidade ou celular...":
            q = ""

        if not q:
            self.filtered_mechanics = list(self.all_mechanics)
        else:
            q_lower = q.lower()
            self.filtered_mechanics = [
                m for m in self.all_mechanics
                if q_lower in m["nome"].lower() or q_lower in m["especialidade"].lower() or q_lower in m["celular"].lower()
            ]
        self._render_table()

    def _render_table(self):
        for child in self.list_inner.winfo_children():
            child.destroy()

        if not self.filtered_mechanics:
            empty_box = tk.Frame(self.list_inner, bg="#1a1f2e", pady=40)
            empty_box.pack(fill="x")
            tk.Label(empty_box, text="Nenhum mecânico encontrado.", font=("Segoe UI", 11), fg="#9ca3af", bg="#1a1f2e").pack()
            return

        for idx, mec in enumerate(self.filtered_mechanics):
            bg_row = "#1c2230" if idx % 2 == 0 else "#161b26"
            row = tk.Frame(self.list_inner, bg=bg_row, padx=16, pady=10, highlightbackground="#2a3245", highlightthickness=1)
            row.pack(fill="x", pady=1)

            row.grid_columnconfigure(0, weight=1, uniform="mec_col")
            row.grid_columnconfigure(1, weight=4, uniform="mec_col")
            row.grid_columnconfigure(2, weight=3, uniform="mec_col")
            row.grid_columnconfigure(3, weight=3, uniform="mec_col")
            row.grid_columnconfigure(4, weight=2, uniform="mec_col")
            row.grid_columnconfigure(5, weight=2, uniform="mec_col")

            # ID
            lbl_id = tk.Label(row, text=f"#{mec['id']}", font=("Consolas", 10, "bold"), fg="#60a5fa", bg=bg_row, anchor="w")
            lbl_id.grid(row=0, column=0, sticky="ew")

            # Nome
            lbl_name = tk.Label(row, text=mec["nome"], font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg=bg_row, anchor="w")
            lbl_name.grid(row=0, column=1, sticky="ew")

            # Especialidade
            lbl_esp = tk.Label(row, text=mec["especialidade"], font=("Segoe UI", 9), fg="#d1d5db", bg=bg_row, anchor="w")
            lbl_esp.grid(row=0, column=2, sticky="ew")

            # Celular
            lbl_cel = tk.Label(row, text=mec.get("celular") or "Não informado", font=("Segoe UI", 9), fg="#9ca3af", bg=bg_row, anchor="w")
            lbl_cel.grid(row=0, column=3, sticky="ew")

            # Status (Badge Ativo / Inativo)
            status_text = "ATIVO" if mec["ativo"] else "INATIVO"
            status_bg = "#064e3b" if mec["ativo"] else "#7f1d1d"
            status_fg = "#34d399" if mec["ativo"] else "#f87171"

            lbl_status = tk.Label(row, text=status_text, font=("Segoe UI", 8, "bold"), fg=status_fg, bg=status_bg, padx=8, pady=2)
            lbl_status.grid(row=0, column=4, sticky="w")

            # Ações (Editar e Excluir)
            act_frame = tk.Frame(row, bg=bg_row)
            act_frame.grid(row=0, column=5, sticky="e")

            btn_e = tk.Button(
                act_frame,
                image=self.img_pencil,
                bg=bg_row,
                activebackground="#22293a",
                bd=0,
                cursor="hand2",
                command=lambda m=mec: self._open_edit_modal(m)
            )
            btn_e.pack(side="left", padx=4)

            btn_d = tk.Button(
                act_frame,
                image=self.img_trash,
                bg=bg_row,
                activebackground="#22293a",
                bd=0,
                cursor="hand2",
                command=lambda m=mec: self._delete_mechanic(m)
            )
            btn_d.pack(side="left", padx=4)

        self.list_inner.update_idletasks()
        self.list_canvas.config(scrollregion=(0, 0, self.list_inner.winfo_width(), self.list_inner.winfo_height()))

    def _open_create_modal(self):
        self._show_mechanic_form_modal(mechanic=None)

    def _open_edit_modal(self, mechanic: Dict[str, Any]):
        self._show_mechanic_form_modal(mechanic=mechanic)

    def _show_mechanic_form_modal(self, mechanic: Optional[Dict[str, Any]] = None):
        """Modal overlay flutuante para criação e edição de mecânicos."""
        is_edit = mechanic is not None

        overlay = tk.Frame(self, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = tk.Frame(overlay, bg="#1a1f2e", highlightbackground="#2563eb", highlightthickness=2, padx=28, pady=24)
        modal.place(relx=0.5, rely=0.5, anchor="center", width=480)

        # Cabeçalho Modal
        title_txt = "Editar Mecânico" if is_edit else "Novo Mecânico / Técnico"
        lbl_title = tk.Label(modal, text=title_txt, font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg="#1a1f2e")
        lbl_title.pack(anchor="w", pady=(0, 16))

        # Variáveis
        var_nome = tk.StringVar(value=mechanic["nome"] if is_edit else "")
        var_especialidade = tk.StringVar(value=mechanic["especialidade"] if is_edit else ESPECIALIDADES_LISTA[1])
        var_celular = tk.StringVar(value=mechanic["celular"] if is_edit else "")
        var_cpf = tk.StringVar(value=mechanic["cpf"] if is_edit else "")
        var_ativo = tk.BooleanVar(value=mechanic["ativo"] if is_edit else True)

        # Máscaras
        def mask_celular(*args):
            raw = "".join(filter(str.isdigit, var_celular.get()))[:11]
            formatted = raw
            if len(raw) > 0:
                formatted = "(" + raw
            if len(raw) > 2:
                formatted = "(" + raw[:2] + ") " + raw[2:]
            if len(raw) > 7:
                formatted = "(" + raw[:2] + ") " + raw[2:7] + "-" + raw[7:]
            if var_celular.get() != formatted:
                var_celular.set(formatted)

        def mask_cpf(*args):
            raw = "".join(filter(str.isdigit, var_cpf.get()))[:11]
            formatted = raw
            if len(raw) > 3:
                formatted = raw[:3] + "." + raw[3:]
            if len(raw) > 6:
                formatted = formatted[:7] + "." + raw[6:]
            if len(raw) > 9:
                formatted = formatted[:11] + "-" + raw[9:]
            if var_cpf.get() != formatted:
                var_cpf.set(formatted)

        var_celular.trace_add("write", mask_celular)
        var_cpf.trace_add("write", mask_cpf)

        # Campo Nome *
        tk.Label(modal, text="Nome Completo *", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        entry_nome = tk.Entry(modal, textvariable=var_nome, font=("Segoe UI", 11), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_nome.pack(fill="x", pady=(0, 12))

        # Campo Especialidade (Dropdown)
        tk.Label(modal, text="Especialidade / Cargo *", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        om_esp = tk.OptionMenu(modal, var_especialidade, *ESPECIALIDADES_LISTA)
        om_esp.config(bg="#0d1117", fg="white", activebackground="#4f77ff", bd=1, highlightthickness=0, font=("Segoe UI", 10))
        om_esp["menu"].config(bg="#1c2230", fg="white")
        om_esp.pack(fill="x", pady=(0, 12))

        # Linha dupla: Celular e CPF
        row_fields = tk.Frame(modal, bg="#1a1f2e")
        row_fields.pack(fill="x", pady=(0, 12))
        row_fields.grid_columnconfigure(0, weight=1)
        row_fields.grid_columnconfigure(1, weight=1)

        f_cel = tk.Frame(row_fields, bg="#1a1f2e")
        f_cel.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Label(f_cel, text="Celular / WhatsApp", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        tk.Entry(f_cel, textvariable=var_celular, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid").pack(fill="x")

        f_cpf = tk.Frame(row_fields, bg="#1a1f2e")
        f_cpf.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        tk.Label(f_cpf, text="CPF", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        tk.Entry(f_cpf, textvariable=var_cpf, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid").pack(fill="x")

        # Checkbox Ativo
        chk_ativo = tk.Checkbutton(
            modal,
            text="Mecânico Ativo no Sistema",
            variable=var_ativo,
            bg="#1a1f2e",
            fg="#ffffff",
            activebackground="#1a1f2e",
            selectcolor="#0d1117",
            font=("Segoe UI", 10)
        )
        chk_ativo.pack(anchor="w", pady=(0, 20))

        # Botões Salvar e Cancelar
        b_box = tk.Frame(modal, bg="#1a1f2e")
        b_box.pack(fill="x")

        def save():
            nome = var_nome.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Preencha o Nome do mecânico.")
                return

            data = {
                "id": mechanic["id"] if is_edit else None,
                "nome": nome,
                "especialidade": var_especialidade.get().strip(),
                "celular": var_celular.get().strip(),
                "cpf": var_cpf.get().strip(),
                "ativo": var_ativo.get()
            }

            MechanicService.save_mechanic(data)
            overlay.destroy()
            self._load_data()

        btn_cancel = tk.Button(b_box, text="Cancelar", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#2a3245", bd=0, padx=16, pady=8, cursor="hand2", command=overlay.destroy)
        btn_cancel.pack(side="left")

        btn_save = tk.Button(b_box, text=" Salvar Mecânico ", font=("Segoe UI", 9, "bold"), fg="white", bg="#10b981", activebackground="#059669", bd=0, padx=20, pady=8, cursor="hand2", command=save)
        btn_save.pack(side="right")

    def _delete_mechanic(self, mechanic: Dict[str, Any]):
        if messagebox.askyesno("Excluir Mecânico", f"Tem certeza que deseja excluir o mecânico '{mechanic['nome']}'?"):
            MechanicService.delete_mechanic(mechanic["id"])
            self._load_data()
