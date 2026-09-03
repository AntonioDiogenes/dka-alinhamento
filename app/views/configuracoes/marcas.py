"""
Tela de Gerenciamento e Edição de Marcas de Veículos (views/configuracoes/marcas.py).
Permite visualizar, buscar e editar marcas existentes. Não permite criar novas marcas.
"""
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any

from app.config.settings import COLORS, FONTS
from app.services.truck_service import TruckService
from app.components.alignment_header import AlignmentHeader
from app.utils.icons import create_icon_image
from app.utils.scroll_helper import setup_canvas_scrolling

class MarcasView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router

        self.all_brands: List[Dict[str, Any]] = []
        self.filtered_brands: List[Dict[str, Any]] = []

        # Ícones
        self.img_search = create_icon_image("search", size=16, color="#8a94a6")
        self.img_clear = create_icon_image("x", size=14, color="#8a94a6")

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # 1. CABEÇALHO TÉCNICO
        self.header = AlignmentHeader(
            self,
            title="Configurações",
            subtitle="Marcas de Veículos (Catálogo)",
            on_back=lambda: self.router.navigate("dashboard"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # 2. BARRA DE BUSCA E FERRAMENTAS (SEM BOTÃO DE CRIAR NOVA)
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
        self.search_box.pack(side="left", fill="x", expand=True)

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

        self.entry_search.insert(0, "Buscar por nome ou código da marca...")
        self.entry_search.config(fg="#8a94a6")

        def on_focus_in(e):
            if self.entry_search.get() == "Buscar por nome ou código da marca...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg="#FFFFFF")

        def on_focus_out(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Buscar por nome ou código da marca...")
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

        # 3. CONTAINER DA TABELA DE MARCAS
        self.table_card = tk.Frame(self, bg="#1a1f2e", highlightbackground="#2a3245", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        # Cabeçalho da Tabela
        self.th_frame = tk.Frame(self.table_card, bg="#111520", padx=16, pady=10)
        self.th_frame.pack(fill="x", side="top")

        self.th_frame.grid_columnconfigure(0, weight=2, uniform="m_col")
        self.th_frame.grid_columnconfigure(1, weight=4, uniform="m_col")
        self.th_frame.grid_columnconfigure(2, weight=3, uniform="m_col")
        self.th_frame.grid_columnconfigure(3, weight=2, uniform="m_col")

        tk.Label(self.th_frame, text="CÓDIGO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(self.th_frame, text="NOME DA MARCA / FABRICANTE", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(self.th_frame, text="MODELOS ASSOCIADOS", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(self.th_frame, text="AÇÃO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="center").grid(row=0, column=3, sticky="ew")

        # Área de Rolagem com Canvas
        self.list_canvas = tk.Canvas(self.table_card, bg="#1a1f2e", highlightthickness=0, bd=0)
        self.list_canvas.pack(fill="both", expand=True, side="top")

        self.list_inner = tk.Frame(self.list_canvas, bg="#1a1f2e")
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")

        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(self.list_window, width=e.width))
        self.list_inner.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        setup_canvas_scrolling(self.list_canvas, self.list_inner)

    def _load_data(self):
        self.all_brands = TruckService.get_brands_summary()
        self._apply_filter()

    def _clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, "Buscar por nome ou código da marca...")
        self.entry_search.config(fg="#8a94a6")
        self._apply_filter()

    def _apply_filter(self):
        q = self.entry_search.get().strip()
        if q == "Buscar por nome ou código da marca...":
            q = ""

        if not q:
            self.filtered_brands = list(self.all_brands)
        else:
            q_lower = q.lower()
            self.filtered_brands = [
                b for b in self.all_brands
                if q_lower in b["brand_name"].lower() or q_lower in b["brand_code"].lower()
            ]
        self._render_table()

    def _render_table(self):
        for child in self.list_inner.winfo_children():
            child.destroy()

        if not self.filtered_brands:
            empty_box = tk.Frame(self.list_inner, bg="#1a1f2e", pady=40)
            empty_box.pack(fill="x")
            tk.Label(empty_box, text="Nenhuma marca encontrada.", font=("Segoe UI", 11), fg="#9ca3af", bg="#1a1f2e").pack()
            return

        for idx, brand in enumerate(self.filtered_brands):
            bg_row = "#1c2230" if idx % 2 == 0 else "#161b26"
            row = tk.Frame(self.list_inner, bg=bg_row, padx=16, pady=10, highlightbackground="#2a3245", highlightthickness=1)
            row.pack(fill="x", pady=1)

            row.grid_columnconfigure(0, weight=2, uniform="m_col")
            row.grid_columnconfigure(1, weight=4, uniform="m_col")
            row.grid_columnconfigure(2, weight=3, uniform="m_col")
            row.grid_columnconfigure(3, weight=2, uniform="m_col")

            # Badge Código
            lbl_code = tk.Label(
                row,
                text=brand["brand_code"],
                font=("Segoe UI", 9, "bold"),
                fg="#60a5fa",
                bg="#0f172a",
                padx=8,
                pady=2
            )
            lbl_code.grid(row=0, column=0, sticky="w")

            # Nome da Marca
            lbl_name = tk.Label(
                row,
                text=brand["brand_name"],
                font=("Segoe UI", 10, "bold"),
                fg="#FFFFFF",
                bg=bg_row
            )
            lbl_name.grid(row=0, column=1, sticky="w")

            # Qtd de Modelos
            lbl_count = tk.Label(
                row,
                text=f"{brand['count']} modelo(s) cadastrado(s)",
                font=("Segoe UI", 9),
                fg="#9ca3af",
                bg=bg_row
            )
            lbl_count.grid(row=0, column=2, sticky="w")

            # Botão Apenas Editar
            btn_edit = tk.Button(
                row,
                text=" ✏️ Editar ",
                font=("Segoe UI", 9, "bold"),
                fg="#FFFFFF",
                bg="#2563eb",
                activebackground="#1d4ed8",
                activeforeground="white",
                bd=0,
                padx=12,
                pady=4,
                cursor="hand2",
                command=lambda b=brand: self._open_edit_modal(b)
            )
            btn_edit.grid(row=0, column=3, sticky="e")

        self.list_inner.update_idletasks()
        self.list_canvas.config(scrollregion=(0, 0, self.list_inner.winfo_width(), self.list_inner.winfo_height()))

    def _open_edit_modal(self, brand: Dict[str, Any]):
        """Abre modal flutuante para editar código e nome da marca."""
        overlay = tk.Frame(self, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = tk.Frame(overlay, bg="#1a1f2e", highlightbackground="#2563eb", highlightthickness=2, padx=28, pady=24)
        modal.place(relx=0.5, rely=0.5, anchor="center", width=440)

        # Cabeçalho Modal
        lbl_title = tk.Label(modal, text="Editar Marca", font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg="#1a1f2e")
        lbl_title.pack(anchor="w", pady=(0, 16))

        # Campo Código
        tk.Label(modal, text="CÓDIGO DA MARCA (3 a 5 LETRAS)", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        entry_code = tk.Entry(modal, font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_code.insert(0, brand["brand_code"])
        entry_code.pack(fill="x", pady=(0, 14))

        # Campo Nome da Marca
        tk.Label(modal, text="NOME DA MARCA / FABRICANTE", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").pack(anchor="w", pady=(0, 4))
        entry_name = tk.Entry(modal, font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_name.insert(0, brand["brand_name"])
        entry_name.pack(fill="x", pady=(0, 20))

        # Botões Salvar e Cancelar
        b_box = tk.Frame(modal, bg="#1a1f2e")
        b_box.pack(fill="x")

        def save():
            new_code = entry_code.get().strip().upper()
            new_name = entry_name.get().strip()

            if not new_code or not new_name:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
                return

            success = TruckService.update_brand(brand["brand_name"], new_name, new_code)
            if success:
                overlay.destroy()
                self._load_data()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar a marca no banco de dados.")

        btn_cancel = tk.Button(b_box, text="Cancelar", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#2a3245", bd=0, padx=14, pady=6, cursor="hand2", command=overlay.destroy)
        btn_cancel.pack(side="left")

        btn_save = tk.Button(b_box, text=" Salvar Alterações ", font=("Segoe UI", 9, "bold"), fg="white", bg="#10b981", activebackground="#059669", bd=0, padx=16, pady=6, cursor="hand2", command=save)
        btn_save.pack(side="right")
