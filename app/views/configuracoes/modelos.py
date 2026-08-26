"""
Tela de Gerenciamento e Edição de Modelos de Veículos (views/configuracoes/modelos.py).
Permite visualizar, buscar, filtrar e editar modelos existentes. Não permite criar novos modelos.
"""
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Any

from app.config.settings import COLORS, FONTS
from app.services.truck_service import TruckService
from app.components.alignment_header import AlignmentHeader
from app.utils.icons import create_icon_image

class ModelosView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router

        self.all_trucks: List[Dict[str, Any]] = []
        self.manufacturers: List[str] = []
        self.filtered_trucks: List[Dict[str, Any]] = []

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
            subtitle="Modelos de Veículos (Catálogo)",
            on_back=lambda: self.router.navigate("dashboard"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # 2. TOOLBAR DE BUSCA E FILTROS (SEM BOTÃO DE CRIAR NOVO)
        self.toolbar_container = tk.Frame(self, bg="#111520", padx=32, pady=16)
        self.toolbar_container.pack(fill="x", side="top")

        self.toolbar = tk.Frame(self.toolbar_container, bg="#111520")
        self.toolbar.pack(fill="x")

        # Campo de Busca por Texto (#0d1117)
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
            font=("Segoe UI", 10)
        )
        self.entry_search.pack(side="left", fill="x", expand=True)

        self.entry_search.insert(0, "Buscar modelo, código ou fabricante...")
        self.entry_search.config(fg="#8a94a6")

        def on_focus_in(e):
            if self.entry_search.get() == "Buscar modelo, código ou fabricante...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg="#FFFFFF")

        def on_focus_out(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Buscar modelo, código ou fabricante...")
                self.entry_search.config(fg="#8a94a6")

        self.entry_search.bind("<FocusIn>", on_focus_in)
        self.entry_search.bind("<FocusOut>", on_focus_out)
        self.entry_search.bind("<KeyRelease>", lambda e: self._apply_filters())

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

        # Filtro por Marca / Fabricante
        self.var_mfg = tk.StringVar(value="Todos os fabricantes")
        self.om_mfg = tk.OptionMenu(self.toolbar, self.var_mfg, "Todos os fabricantes", command=lambda val: self._apply_filters())
        self.om_mfg.config(
            bg="#0d1117",
            fg="#FFFFFF",
            activebackground="#1c2230",
            activeforeground="white",
            bd=1,
            highlightbackground="#2a3245",
            highlightthickness=1,
            font=("Segoe UI", 10),
            padx=14,
            pady=4
        )
        self.om_mfg["menu"].config(bg="#1c2230", fg="white", activebackground="#4f77ff")
        self.om_mfg.pack(side="left")

        # 3. CONTAINER DA TABELA DE MODELOS
        self.table_card = tk.Frame(self, bg="#1a1f2e", highlightbackground="#2a3245", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        # Cabeçalho da Tabela
        self.th_frame = tk.Frame(self.table_card, bg="#111520", padx=16, pady=10)
        self.th_frame.pack(fill="x", side="top")

        self.th_frame.grid_columnconfigure(0, weight=3, uniform="mod_col")
        self.th_frame.grid_columnconfigure(1, weight=2, uniform="mod_col")
        self.th_frame.grid_columnconfigure(2, weight=2, uniform="mod_col")
        self.th_frame.grid_columnconfigure(3, weight=2, uniform="mod_col")
        self.th_frame.grid_columnconfigure(4, weight=2, uniform="mod_col")
        self.th_frame.grid_columnconfigure(5, weight=2, uniform="mod_col")

        tk.Label(self.th_frame, text="NOME DO MODELO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(self.th_frame, text="MARCA / FABRICANTE", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(self.th_frame, text="CATEGORIA", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(self.th_frame, text="ARO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="center").grid(row=0, column=3, sticky="ew")
        tk.Label(self.th_frame, text="EIXOS", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="center").grid(row=0, column=4, sticky="ew")
        tk.Label(self.th_frame, text="AÇÃO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#111520", anchor="center").grid(row=0, column=5, sticky="ew")

        # Área de Rolagem com Canvas
        self.list_canvas = tk.Canvas(self.table_card, bg="#1a1f2e", highlightthickness=0, bd=0)
        self.list_canvas.pack(fill="both", expand=True, side="top")

        self.list_inner = tk.Frame(self.list_canvas, bg="#1a1f2e")
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")

        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(self.list_window, width=e.width))

    def _load_data(self):
        self.all_trucks = TruckService.get_all_trucks()
        self.manufacturers = TruckService.get_manufacturers()

        # Atualizar opções do OptionMenu
        menu = self.om_mfg["menu"]
        menu.delete(0, "end")
        for m in self.manufacturers:
            menu.add_command(label=m, command=lambda value=m: self._on_mfg_selected(value))

        self._apply_filters()

    def _on_mfg_selected(self, val: str):
        self.var_mfg.set(val)
        self._apply_filters()

    def _clear_search(self):
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, "Buscar modelo, código ou fabricante...")
        self.entry_search.config(fg="#8a94a6")
        self.var_mfg.set("Todos os fabricantes")
        self._apply_filters()

    def _apply_filters(self):
        q = self.entry_search.get().strip()
        if q == "Buscar modelo, código ou fabricante...":
            q = ""

        mfg_val = self.var_mfg.get().strip()

        self.filtered_trucks = TruckService.filter_trucks(
            search_text=q,
            manufacturer=mfg_val
        )
        self._render_table()

    def _render_table(self):
        for child in self.list_inner.winfo_children():
            child.destroy()

        if not self.filtered_trucks:
            empty_box = tk.Frame(self.list_inner, bg="#1a1f2e", pady=40)
            empty_box.pack(fill="x")
            tk.Label(empty_box, text="Nenhum modelo encontrado.", font=("Segoe UI", 11), fg="#9ca3af", bg="#1a1f2e").pack()
            return

        for idx, truck in enumerate(self.filtered_trucks):
            bg_row = "#1c2230" if idx % 2 == 0 else "#161b26"
            row = tk.Frame(self.list_inner, bg=bg_row, padx=16, pady=8, highlightbackground="#2a3245", highlightthickness=1)
            row.pack(fill="x", pady=1)

            row.grid_columnconfigure(0, weight=3, uniform="mod_col")
            row.grid_columnconfigure(1, weight=2, uniform="mod_col")
            row.grid_columnconfigure(2, weight=2, uniform="mod_col")
            row.grid_columnconfigure(3, weight=2, uniform="mod_col")
            row.grid_columnconfigure(4, weight=2, uniform="mod_col")
            row.grid_columnconfigure(5, weight=2, uniform="mod_col")

            # Nome do Modelo
            lbl_name = tk.Label(row, text=truck["model_name"], font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg=bg_row, anchor="w")
            lbl_name.grid(row=0, column=0, sticky="ew")

            # Marca
            lbl_brand = tk.Label(row, text=f"{truck['brand_name']} ({truck['brand_code']})", font=("Segoe UI", 9, "bold"), fg="#60a5fa", bg=bg_row, anchor="w")
            lbl_brand.grid(row=0, column=1, sticky="ew")

            # Categoria
            lbl_cat = tk.Label(row, text=truck.get("category", "TRUCK"), font=("Segoe UI", 9), fg="#9ca3af", bg=bg_row, anchor="w")
            lbl_cat.grid(row=0, column=2, sticky="ew")

            # Aro
            lbl_rim = tk.Label(row, text=f"{truck['rim_size']}\"", font=("Segoe UI", 9, "bold"), fg="#e5e7eb", bg=bg_row, anchor="center")
            lbl_rim.grid(row=0, column=3, sticky="ew")

            # Eixos
            lbl_axles = tk.Label(row, text=f"{truck['axles_count']} eixos", font=("Segoe UI", 9), fg="#9ca3af", bg=bg_row, anchor="center")
            lbl_axles.grid(row=0, column=4, sticky="ew")

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
                command=lambda t=truck: self._open_edit_modal(t)
            )
            btn_edit.grid(row=0, column=5, sticky="e")

        self.list_inner.update_idletasks()
        self.list_canvas.config(scrollregion=(0, 0, self.list_inner.winfo_width(), self.list_inner.winfo_height()))

    def _open_edit_modal(self, truck: Dict[str, Any]):
        """Abre modal flutuante para editar dados do modelo."""
        overlay = tk.Frame(self, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = tk.Frame(overlay, bg="#1a1f2e", highlightbackground="#2563eb", highlightthickness=2, padx=28, pady=24)
        modal.place(relx=0.5, rely=0.5, anchor="center", width=480)

        # Título
        lbl_title = tk.Label(modal, text=f"Editar Modelo: {truck['model_name']}", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#1a1f2e")
        lbl_title.pack(anchor="w", pady=(0, 16))

        # 1. Nome do Modelo
        tk.Label(modal, text="NOME DO MODELO", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").pack(anchor="w", pady=(0, 2))
        entry_model = tk.Entry(modal, font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_model.insert(0, truck["model_name"])
        entry_model.pack(fill="x", pady=(0, 12))

        # 2. Marca / Fabricante
        f_brand = tk.Frame(modal, bg="#1a1f2e")
        f_brand.pack(fill="x", pady=(0, 12))

        f_brand.columnconfigure(0, weight=3)
        f_brand.columnconfigure(1, weight=1)

        tk.Label(f_brand, text="NOME DA MARCA", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").grid(row=0, column=0, sticky="w", pady=(0, 2))
        tk.Label(f_brand, text="CÓDIGO", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").grid(row=0, column=1, sticky="w", pady=(0, 2))

        entry_brand_name = tk.Entry(f_brand, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_brand_name.insert(0, truck["brand_name"])
        entry_brand_name.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        entry_brand_code = tk.Entry(f_brand, font=("Segoe UI", 10, "bold"), fg="#60a5fa", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_brand_code.insert(0, truck["brand_code"])
        entry_brand_code.grid(row=1, column=1, sticky="ew")

        # 3. Categoria, Aro e Eixos
        f_specs = tk.Frame(modal, bg="#1a1f2e")
        f_specs.pack(fill="x", pady=(0, 18))

        f_specs.columnconfigure(0, weight=2)
        f_specs.columnconfigure(1, weight=1)
        f_specs.columnconfigure(2, weight=1)

        tk.Label(f_specs, text="CATEGORIA", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").grid(row=0, column=0, sticky="w", pady=(0, 2))
        tk.Label(f_specs, text="ARO (\")", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").grid(row=0, column=1, sticky="w", pady=(0, 2))
        tk.Label(f_specs, text="QTD EIXOS", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e").grid(row=0, column=2, sticky="w", pady=(0, 2))

        entry_cat = tk.Entry(f_specs, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid")
        entry_cat.insert(0, truck.get("category", "TRUCK"))
        entry_cat.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        entry_rim = tk.Entry(f_specs, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid", justify="center")
        entry_rim.insert(0, str(truck.get("rim_size", "22")))
        entry_rim.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        entry_axles = tk.Entry(f_specs, font=("Segoe UI", 10), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, relief="solid", justify="center")
        entry_axles.insert(0, str(truck.get("axles_count", 3)))
        entry_axles.grid(row=1, column=2, sticky="ew")

        # Botões Salvar e Cancelar
        b_box = tk.Frame(modal, bg="#1a1f2e")
        b_box.pack(fill="x")

        def save():
            m_name = entry_model.get().strip()
            b_name = entry_brand_name.get().strip()
            b_code = entry_brand_code.get().strip().upper()
            cat = entry_cat.get().strip()
            rim = entry_rim.get().strip()
            axles_raw = entry_axles.get().strip()

            if not m_name or not b_name or not b_code:
                messagebox.showwarning("Aviso", "Preencha o nome do modelo e dados da marca.")
                return

            try:
                axles_val = int(axles_raw)
            except ValueError:
                messagebox.showwarning("Aviso", "Quantidade de eixos deve ser um número inteiro.")
                return

            update_payload = {
                "model_name": m_name,
                "brand_name": b_name,
                "brand_code": b_code,
                "category": cat,
                "rim_size": rim,
                "axles_count": axles_val
            }

            success = TruckService.update_model(truck["id"], update_payload)
            if success:
                overlay.destroy()
                self._load_data()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o modelo no banco de dados.")

        btn_cancel = tk.Button(b_box, text="Cancelar", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#2a3245", bd=0, padx=14, pady=6, cursor="hand2", command=overlay.destroy)
        btn_cancel.pack(side="left")

        btn_save = tk.Button(b_box, text=" Salvar Alterações ", font=("Segoe UI", 9, "bold"), fg="white", bg="#10b981", activebackground="#059669", bd=0, padx=16, pady=6, cursor="hand2", command=save)
        btn_save.pack(side="right")
