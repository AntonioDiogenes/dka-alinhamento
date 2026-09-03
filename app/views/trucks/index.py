"""
Tela 1 do Fluxo de Alinhamento: Seleção de Truck Desktop (views/trucks/index.py).
Estética Dark Mode Técnico #111520 com cartões bicolores de 128px, AlignmentHeader #001f3f, toolbar de busca/fabricantes, overlay de carregamento e paginação transparente.
"""
import math
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional

from app.config.settings import COLORS
from app.services.truck_service import TruckService
from app.components.alignment_header import AlignmentHeader
from app.components.truck_card import TruckCard
from app.utils.icons import create_icon_image

class TrucksIndexView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router

        # Dados e Paginação
        self.all_trucks: List[Dict[str, Any]] = TruckService.get_all_trucks()
        self.manufacturers: List[str] = TruckService.get_manufacturers()
        self.filtered_trucks: List[Dict[str, Any]] = list(self.all_trucks)
        self.page_size = 9
        self.current_page = 1
        self.is_loading = False

        # Ícones
        self.img_search = create_icon_image("search", size=16, color="#8a94a6")
        self.img_clear = create_icon_image("x", size=14, color="#8a94a6")
        self.img_prev = create_icon_image("chevron_left", size=18, color="#FFFFFF")
        self.img_next = create_icon_image("chevron_right", size=18, color="#FFFFFF")

        self._build_ui()
        self._apply_filters()

    def _build_ui(self):
        # ==========================================
        # 1. CABEÇALHO ESPECIALIZADO (AlignmentHeader #001f3f)
        # ==========================================
        self.header = AlignmentHeader(
            self,
            title="Alinhamento",
            subtitle="Selecione o veículo",
            on_back=lambda: self.router.navigate("dashboard"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # ==========================================
        # 2. TOOLBAR DE BUSCA E FILTROS DE FABRICANTE
        # ==========================================
        self.toolbar_container = tk.Frame(self, bg="#111520", padx=32, pady=16)
        self.toolbar_container.pack(fill="x", side="top")

        self.toolbar = tk.Frame(self.toolbar_container, bg="#111520")
        self.toolbar.pack(fill="x")

        # Colunas 1 a 4: Campo de Busca por Texto (#0d1117)
        self.search_box = tk.Frame(
            self.toolbar,
            bg="#0d1117",
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=12,
            pady=8
        )
        self.search_box.pack(side="left", fill="x", expand=True, padx=(0, 16))

        lbl_search_icon = tk.Label(self.search_box, image=self.img_search, bg="#0d1117")
        lbl_search_icon.pack(side="left", padx=(0, 8))

        self.var_search = tk.StringVar()
        self.entry_search = tk.Entry(
            self.search_box,
            textvariable=self.var_search,
            bg="#0d1117",
            fg="#FFFFFF",
            insertbackground="white",
            bd=0,
            font=("Segoe UI", 11)
        )
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=4)

        # Placeholder
        self.entry_search.insert(0, "Procurar modelo...")
        self.entry_search.config(fg="#8a94a6")

        def on_focus_in(e):
            if self.entry_search.get() == "Procurar modelo...":
                self.entry_search.delete(0, tk.END)
                self.entry_search.config(fg="#FFFFFF")

        def on_focus_out(e):
            if not self.entry_search.get():
                self.entry_search.insert(0, "Procurar modelo...")
                self.entry_search.config(fg="#8a94a6")

        self.entry_search.bind("<FocusIn>", on_focus_in)
        self.entry_search.bind("<FocusOut>", on_focus_out)
        self.entry_search.bind("<KeyRelease>", lambda e: self._on_filter_changed())

        # Botão Limpar Texto Digitado (X)
        self.btn_clear_text = tk.Button(
            self.search_box,
            image=self.img_clear,
            bg="#0d1117",
            activebackground="#1c2230",
            bd=0,
            cursor="hand2",
            command=self._clear_search_text
        )
        self.btn_clear_text.pack(side="right")

        # Colunas 5 a 8: Filtro Seleção de Fabricante
        self.var_mfg = tk.StringVar(value="Todos os fabricantes")

        def _show_mfg_menu():
            menu = tk.Menu(self, tearoff=0, bg="#1c2230", fg="white", activebackground="#4f77ff", font=("Segoe UI", 10))
            for mfg in self.manufacturers:
                def make_cmd(val=mfg):
                    self.var_mfg.set(val)
                    self.btn_mfg.config(text=f" {val}  ▾ ")
                    self._on_filter_changed()
                menu.add_command(label=f"  {mfg}  ", command=make_cmd)
            x = self.btn_mfg.winfo_rootx()
            y = self.btn_mfg.winfo_rooty() + self.btn_mfg.winfo_height() + 2
            menu.post(x, y)

        self.btn_mfg = tk.Button(
            self.toolbar,
            text=f" {self.var_mfg.get()}  ▾ ",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg="#0d1117",
            activebackground="#1c2230",
            activeforeground="white",
            bd=1,
            relief="solid",
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=14,
            pady=5,
            cursor="hand2",
            command=_show_mfg_menu
        )
        self.btn_mfg.pack(side="left", padx=(0, 16))

        # ==========================================
        # 3. GRADE CENTRAL DE CAMINHÕES (3 COLUNAS)
        # ==========================================
        self.grid_container = tk.Frame(self, bg="#111520", padx=32, pady=8)
        self.grid_container.pack(fill="both", expand=True)

        self.cards_area = tk.Frame(self.grid_container, bg="#111520")
        self.cards_area.pack(fill="both", expand=True)

        # Configurar 3 Colunas de Tamanho Igual no Desktop
        self.cards_area.grid_columnconfigure(0, weight=1)
        self.cards_area.grid_columnconfigure(1, weight=1)
        self.cards_area.grid_columnconfigure(2, weight=1)

        # ==========================================
        # 4. RODAPÉ TRANSPARENTE
        # ==========================================
        self.footer = tk.Frame(self, bg="#111520", padx=32, pady=16)
        self.footer.pack(fill="x", side="bottom")

        self.lbl_counter = tk.Label(
            self.footer,
            text="",
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#111520"
        )
        self.lbl_counter.pack(side="left")

        self.nav_frame = tk.Frame(self.footer, bg="#111520")
        self.nav_frame.pack(side="right")

        self.btn_prev = tk.Button(
            self.nav_frame,
            image=self.img_prev,
            bg="#1a1f2e",
            activebackground="#4f77ff",
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
            fg="#FFFFFF",
            bg="#111520",
            padx=8
        )
        self.lbl_page_num.pack(side="left")

        self.btn_next = tk.Button(
            self.nav_frame,
            image=self.img_next,
            bg="#1a1f2e",
            activebackground="#4f77ff",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._next_page
        )
        self.btn_next.pack(side="left", padx=4)

    def _clear_search_text(self):
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, "Procurar modelo...")
        self.entry_search.config(fg="#8a94a6")
        self.current_page = 1
        self._apply_filters()

    def _on_filter_changed(self):
        self.current_page = 1
        self._apply_filters()

    def _apply_filters(self):
        search_val = self.entry_search.get().strip()
        if search_val == "Procurar modelo...":
            search_val = ""

        mfg_val = self.var_mfg.get().strip()

        self.filtered_trucks = TruckService.filter_trucks(
            search_text=search_val,
            manufacturer=mfg_val
        )
        self._render_cards()

    def _render_cards(self):
        for child in self.cards_area.winfo_children():
            child.destroy()

        total = len(self.filtered_trucks)

        # Estado Vazio (Sem resultados)
        if total == 0:
            empty_box = tk.Frame(self.cards_area, bg="#111520", pady=64)
            empty_box.grid(row=0, column=0, columnspan=3, sticky="nsew")

            lbl_empty_icon = tk.Label(
                empty_box,
                text="🔍",
                font=("Segoe UI", 48),
                fg="#3b4252",
                bg="#111520"
            )
            lbl_empty_icon.pack()

            lbl_empty_msg = tk.Label(
                empty_box,
                text="Nenhum veículo encontrado",
                font=("Segoe UI", 13, "bold"),
                fg="#FFFFFF",
                bg="#111520"
            )
            lbl_empty_msg.pack(pady=(12, 4))

            lbl_empty_sub = tk.Label(
                empty_box,
                text="Tente ajustar seus filtros de busca",
                font=("Segoe UI", 10),
                fg="#9ca3af",
                bg="#111520"
            )
            lbl_empty_sub.pack()

            self._update_pagination(0, 0, 0)
            return

        total_pages = math.ceil(total / self.page_size) or 1
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total)
        page_items = self.filtered_trucks[start_idx:end_idx]

        for idx, item in enumerate(page_items):
            r = idx // 3
            c = idx % 3

            card = TruckCard(
                self.cards_area,
                truck_data=item,
                on_click=self._on_select_truck
            )
            card.grid(row=r, column=c, sticky="ew", padx=8, pady=8)

        self._update_pagination(start_idx + 1, end_idx, total)

    def _update_pagination(self, start: int, end: int, total: int):
        if total == 0:
            self.lbl_counter.config(text="Exibindo 0 registros")
            self.lbl_page_num.config(text="Página 0 de 0")
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            total_pages = math.ceil(total / self.page_size)
            self.lbl_counter.config(text=f"Exibindo {total} registros")
            self.lbl_page_num.config(text=f"Página {self.current_page} de {total_pages}")
            self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
            self.btn_next.config(state="normal" if self.current_page < total_pages else "disabled")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_cards()

    def _next_page(self):
        total_pages = math.ceil(len(self.filtered_trucks) / self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_cards()

    def _on_select_truck(self, truck_data: Dict[str, Any]):
        """Exibe o Overlay de Carregamento ('Carregando eixos...') e avança."""
        if self.is_loading:
            return

        self.is_loading = True
        overlay = tk.Frame(self, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = tk.Frame(overlay, bg="#1a1f2e", highlightbackground="#4f77ff", highlightthickness=1, padx=40, pady=32)
        modal.place(relx=0.5, rely=0.5, anchor="center")

        lbl_spin = tk.Label(modal, text="⏳", font=("Segoe UI", 32), bg="#1a1f2e")
        lbl_spin.pack()

        lbl_txt = tk.Label(
            modal,
            text=f"Carregando eixos para {truck_data['brand_name']} {truck_data['model_name']}...",
            font=("Segoe UI", 11, "bold"),
            fg="#FFFFFF",
            bg="#1a1f2e"
        )
        lbl_txt.pack(pady=(16, 0))

        # Simula o carregamento e transição após 1.2s
        self.after(1200, lambda: self._finish_loading(overlay, truck_data))

    def _finish_loading(self, overlay: tk.Frame, truck_data: Dict[str, Any]):
        overlay.destroy()
        self.is_loading = False
        # Redireciona para a Tela 2: Composição do Veículo e Configuração de Eixos
        self.router.navigate("trucks.setup", truck_data=truck_data)
