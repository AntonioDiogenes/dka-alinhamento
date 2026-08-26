"""
Tela 2: Composição do Veículo e Configuração de Eixos (views/trucks/setup.py).
Layout Split-Screen em 2 Colunas:
- Coluna Esquerda: Formulário de Unidades (Cards em Scroll).
- Coluna Direita: TruckChassisPreview (Diagrama dinâmico em tempo real do chassi) + Botão Fixo no Canto Inferior Direito (AVANÇAR PARA MEDIÇÃO FÍSICA).
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Dict, Any

from app.config.settings import COLORS, FONTS
from app.components.alignment_header import AlignmentHeader
from app.components.truck_chassis_preview import TruckChassisPreview
from app.utils.icons import create_icon_image

UNIT_TYPES = [
    "Cavalo Mecânico", "Caminhão Rígido", "Semirreboque", "Reboque", "Dolly", "Implemento"
]

CATALOG_OPTIONS = [
    "Volvo FH 540 Globetrotter", "Scania R450 6x2", "Mercedes-Benz Actros 2651",
    "DAF XF 530 6x4", "MAN TGX 28.440", "Iveco Hi-Way 600S44T", "Universal"
]

class TrucksSetupView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router
        self.kwargs = kwargs or {}

        # Obter veículo selecionado no Catálogo (Tela 1)
        truck_info = self.kwargs.get("truck_data") or self.kwargs.get("truck") or {}

        if truck_info:
            brand = truck_info.get("brand_name", "")
            model = truck_info.get("model_name", "Caminhão")
            catalog_title = f"{brand} {model}".strip()
            category = str(truck_info.get("category", "")).upper()
            total_axles = int(truck_info.get("axles_count", 3))

            is_rigid = any(k in category or k in model.upper() for k in ["RIGID", "RÍGIDO", "RIGIDO", "TOCO", "3/4", "CHASSI"])
            unit1_type = "Caminhão Rígido" if is_rigid else "Cavalo Mecânico"
            front = 2 if "BIDIRECIONAL" in category or "8X" in category else 1
            rear = max(1, total_axles - front)

            # Carrega SEMPRE apenas a 1ª unidade selecionada (sem reboque padrão)
            self.units_data: List[Dict[str, Any]] = [
                {
                    "id": 1,
                    "type": unit1_type,
                    "catalog": catalog_title,
                    "front_axles": front,
                    "rear_axles": rear,
                    "total_axles": front + rear
                }
            ]
        else:
            # Estado Inicial Padrão (Sempre 1 única unidade)
            self.units_data: List[Dict[str, Any]] = [
                {
                    "id": 1,
                    "type": "Cavalo Mecânico",
                    "catalog": "Volvo FH 540 Globetrotter",
                    "front_axles": 1,
                    "rear_axles": 2,
                    "total_axles": 3
                }
            ]

        # Ícones
        self.img_trash = create_icon_image("trash", size=16, color="#ef4444")
        self.img_plus = create_icon_image("plus", size=18, color="#60a5fa")
        self.img_info = create_icon_image("info", size=16, color="#60a5fa")
        self.img_next = create_icon_image("chevron_right", size=20, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # ==========================================
        # 1. CABEÇALHO ESPECIALIZADO (AlignmentHeader)
        # ==========================================
        self.header = AlignmentHeader(
            self,
            title="Alinhamento",
            subtitle="Monte a composição veicular e ajuste os eixos",
            on_back=lambda: self.router.navigate("trucks"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # ==========================================
        # 2. ÁREA DE TRABALHO SPLIT-SCREEN (50% / 50%)
        # ==========================================
        self.split_container = tk.Frame(self, bg="#111520")
        self.split_container.pack(fill="both", expand=True)

        self.split_container.grid_columnconfigure(0, weight=1) # Coluna Esquerda (50%)
        self.split_container.grid_columnconfigure(1, weight=1) # Coluna Direita (50%)
        self.split_container.grid_rowconfigure(0, weight=1)

        # ------------------------------------------
        # COLUNA ESQUERDA: FORMULÁRIO DE UNIDADES
        # ------------------------------------------
        self.left_col = tk.Frame(self.split_container, bg="#111520", padx=24, pady=20)
        self.left_col.grid(row=0, column=0, sticky="nsew")

        # Scroll Canvas para o formulário de unidades
        self.canvas_form = tk.Canvas(self.left_col, bg="#111520", highlightthickness=0, bd=0)
        self.scrollbar_form = ttk.Scrollbar(self.left_col, orient="vertical", command=self.canvas_form.yview)
        self.form_inner = tk.Frame(self.canvas_form, bg="#111520")

        self.canvas_form.create_window((0, 0), window=self.form_inner, anchor="nw")
        self.canvas_form.configure(yscrollcommand=self.scrollbar_form.set)

        self.canvas_form.pack(side="left", fill="both", expand=True)
        self.scrollbar_form.pack(side="right", fill="y")

        self.form_inner.bind("<Configure>", lambda e: self.canvas_form.configure(scrollregion=self.canvas_form.bbox("all")))
        self.canvas_form.bind("<Configure>", lambda e: self.canvas_form.itemconfig(self.canvas_form.find_withtag("all")[0], width=e.width))

        # ------------------------------------------
        # COLUNA DIREITA: TRUCK CHASSIS PREVIEW + BOTÃO NO CANTO INFERIOR DIREITO
        # ------------------------------------------
        self.right_col = tk.Frame(self.split_container, bg="#0d1117", padx=24, pady=20)
        self.right_col.grid(row=0, column=1, sticky="nsew")

        # BOTÃO FIXO NO CANTO INFERIOR DIREITO (AVANÇAR PARA MEDIÇÃO FÍSICA)
        self.btn_advance = tk.Button(
            self.right_col,
            text=" AVANÇAR PARA MEDIÇÃO FÍSICA ",
            image=self.img_next,
            compound="right",
            font=("Segoe UI", 11, "bold"),
            fg="#FFFFFF",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            padx=20,
            pady=14,
            cursor="hand2",
            command=self._advance_to_medicao
        )
        self.btn_advance.pack(side="bottom", fill="x", pady=(16, 0))

        # Renderizador dinâmico do diagrama do chassi (preenche a área restante da direita)
        self.chassis_preview = TruckChassisPreview(self.right_col, units_data=self.units_data)
        self.chassis_preview.pack(fill="both", expand=True)

        # Renderizar lista inicial de unidades
        self._render_unit_cards()

    def _render_unit_cards(self):
        for child in self.form_inner.winfo_children():
            child.destroy()

        # Título da Seção Esquerda
        lbl_sec_title = tk.Label(
            self.form_inner,
            text="Unidades da Composição Veicular",
            font=("Segoe UI", 12, "bold"),
            fg="#FFFFFF",
            bg="#111520"
        )
        lbl_sec_title.pack(anchor="w", pady=(0, 16))

        # Renderizar cada cartão de unidade
        for idx, unit in enumerate(self.units_data):
            card = self._create_unit_card(idx, unit)
            card.pack(fill="x", pady=(0, 16))

        # Botão "+ Add Acoplamento"
        btn_add_coupling = tk.Button(
            self.form_inner,
            text=" +  Add Acoplamento (Semirreboque / Dolly) ",
            font=("Segoe UI", 10, "bold"),
            fg="#60a5fa",
            bg="#161b26",
            activebackground="#1e293b",
            activeforeground="#93c5fd",
            bd=1,
            relief="solid",
            highlightbackground="#2563eb",
            padx=16,
            pady=12,
            cursor="hand2",
            command=self._add_coupling_unit
        )
        btn_add_coupling.pack(fill="x", pady=(8, 20))

        # Atualizar Diagrama da Direita
        self.chassis_preview.update_composition(self.units_data)

    def _create_unit_card(self, idx: int, unit: Dict[str, Any]) -> tk.Frame:
        card = tk.Frame(
            self.form_inner,
            bg="#161b26",
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=16,
            pady=14
        )

        # Cabeçalho do Card (Badge de Tipo + Botão Lixeira)
        card_hdr = tk.Frame(card, bg="#161b26")
        card_hdr.pack(fill="x", pady=(0, 12))

        # Dropdown / Selector de Tipo de Unidade
        var_type = tk.StringVar(value=unit["type"])
        om_type = tk.OptionMenu(
            card_hdr,
            var_type,
            *UNIT_TYPES,
            command=lambda val, i=idx: self._on_type_changed(i, val)
        )
        om_type.config(
            font=("Segoe UI", 10, "bold"),
            fg="#60a5fa",
            bg="#1c2538",
            activebackground="#2563eb",
            activeforeground="white",
            bd=0,
            highlightthickness=0,
            indicatoron=1,
            padx=8,
            pady=4
        )
        om_type.pack(side="left")

        # Botão Lixeira (Permitido remover apenas se houver mais de 1 unidade)
        if len(self.units_data) > 1:
            btn_remove = tk.Button(
                card_hdr,
                image=self.img_trash,
                bg="#161b26",
                activebackground="#2a3245",
                bd=0,
                cursor="hand2",
                command=lambda i=idx: self._remove_unit(i)
            )
            btn_remove.pack(side="right")

        # Dropdown de Catálogo / Modelo de Referência
        lbl_cat = tk.Label(card, text="Modelo / Catálogo de Referência", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#161b26")
        lbl_cat.pack(anchor="w", pady=(0, 4))

        var_cat = tk.StringVar(value=unit["catalog"])
        om_cat = tk.OptionMenu(
            card,
            var_cat,
            *CATALOG_OPTIONS,
            command=lambda val, i=idx: self._on_catalog_changed(i, val)
        )
        om_cat.config(
            font=("Segoe UI", 9),
            fg="#FFFFFF",
            bg="#0d1117",
            activebackground="#1e293b",
            bd=1,
            highlightbackground="#2a3245",
            anchor="w"
        )
        om_cat.pack(fill="x", pady=(0, 12))

        # Linha de Contadores de Eixos (Dianteiros vs Traseiros)
        is_trailer = unit["type"] in ["Semirreboque", "Reboque", "Dolly", "Implemento"]

        axles_row = tk.Frame(card, bg="#161b26")
        axles_row.pack(fill="x")

        # Contador de Eixos Dianteiros (Ocultado para Semirreboques/Reboques)
        if not is_trailer:
            f_box = tk.Frame(axles_row, bg="#0d1117", padx=12, pady=8, highlightbackground="#2a3245", highlightthickness=1)
            f_box.pack(side="left", fill="x", expand=True, padx=(0, 6))

            tk.Label(f_box, text="Eixos Dianteiros", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#0d1117").pack(anchor="w")

            f_ctrl = tk.Frame(f_box, bg="#0d1117")
            f_ctrl.pack(fill="x", pady=(4, 0))

            btn_f_minus = tk.Button(f_ctrl, text="-", font=("Segoe UI", 11, "bold"), fg="white", bg="#2a3245", activebackground="#3b4252", bd=0, width=2, command=lambda i=idx: self._adjust_axles(i, "front", -1))
            btn_f_minus.pack(side="left")

            lbl_f_val = tk.Label(f_ctrl, text=str(unit["front_axles"]), font=("Segoe UI", 12, "bold"), fg="#60a5fa", bg="#0d1117", width=4)
            lbl_f_val.pack(side="left")

            btn_f_plus = tk.Button(f_ctrl, text="+", font=("Segoe UI", 11, "bold"), fg="white", bg="#2a3245", activebackground="#3b4252", bd=0, width=2, command=lambda i=idx: self._adjust_axles(i, "front", 1))
            btn_f_plus.pack(side="left")

        # Contador de Eixos Traseiros
        r_box = tk.Frame(axles_row, bg="#0d1117", padx=12, pady=8, highlightbackground="#2a3245", highlightthickness=1)
        r_box.pack(side="left", fill="x", expand=True, padx=(6 if not is_trailer else 0, 0))

        tk.Label(r_box, text="Eixos Traseiros", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#0d1117").pack(anchor="w")

        r_ctrl = tk.Frame(r_box, bg="#0d1117")
        r_ctrl.pack(fill="x", pady=(4, 0))

        btn_r_minus = tk.Button(r_ctrl, text="-", font=("Segoe UI", 11, "bold"), fg="white", bg="#2a3245", activebackground="#3b4252", bd=0, width=2, command=lambda i=idx: self._adjust_axles(i, "rear", -1))
        btn_r_minus.pack(side="left")

        lbl_r_val = tk.Label(r_ctrl, text=str(unit["rear_axles"]), font=("Segoe UI", 12, "bold"), fg="#10b981", bg="#0d1117", width=4)
        lbl_r_val.pack(side="left")

        btn_r_plus = tk.Button(r_ctrl, text="+", font=("Segoe UI", 11, "bold"), fg="white", bg="#2a3245", activebackground="#3b4252", bd=0, width=2, command=lambda i=idx: self._adjust_axles(i, "rear", 1))
        btn_r_plus.pack(side="left")

        return card

    def _on_type_changed(self, idx: int, new_type: str):
        self.units_data[idx]["type"] = new_type
        if new_type in ["Semirreboque", "Reboque", "Dolly", "Implemento"]:
            self.units_data[idx]["front_axles"] = 0
        elif self.units_data[idx]["front_axles"] == 0:
            self.units_data[idx]["front_axles"] = 1

        self.units_data[idx]["total_axles"] = self.units_data[idx]["front_axles"] + self.units_data[idx]["rear_axles"]
        self._render_unit_cards()

    def _on_catalog_changed(self, idx: int, new_catalog: str):
        self.units_data[idx]["catalog"] = new_catalog

    def _adjust_axles(self, idx: int, position: str, delta: int):
        unit = self.units_data[idx]
        if position == "front":
            new_val = max(1 if unit["type"] not in ["Semirreboque", "Reboque", "Dolly"] else 0, unit["front_axles"] + delta)
            unit["front_axles"] = min(3, new_val)
        else:
            new_val = max(1, unit["rear_axles"] + delta)
            unit["rear_axles"] = min(5, new_val)

        unit["total_axles"] = unit["front_axles"] + unit["rear_axles"]
        self._render_unit_cards()

    def _add_coupling_unit(self):
        new_id = len(self.units_data) + 1
        self.units_data.append({
            "id": new_id,
            "type": "Semirreboque",
            "catalog": "Universal",
            "front_axles": 0,
            "rear_axles": 3,
            "total_axles": 3
        })
        self._render_unit_cards()

    def _remove_unit(self, idx: int):
        if len(self.units_data) > 1:
            self.units_data.pop(idx)
            for i, u in enumerate(self.units_data, start=1):
                u["id"] = i
            self._render_unit_cards()

    def _advance_to_medicao(self):
        # Transiciona para a Tela 3: Medição Física de Eixos (medidas.py)
        self.router.navigate("trucks.medidas", composition_units=self.units_data)
