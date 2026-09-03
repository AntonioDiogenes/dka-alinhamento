"""
Tela 3 do Fluxo de Alinhamento: Medição Física de Eixos (views/trucks/medidas.py).
Recursos:
- Header Técnico e Barra de Abas de Estado (MEDIÇÃO INICIAL Antes vs MEDIÇÃO FINAL Depois).
- Grade Dinâmica de 3 Colunas: Cartões de Medição Direta (MeasurementCard), Tolerância Inteligente Verde/Vermelho (ToleranceCard) e Indicadores de Inclinação de Rodas (AlignmentIndicator).
- Matriz Dinâmica de Eixo Dianteiro Direcional vs Eixo Traseiro Tração/Carreta.
- Painel Lateral Fixo de Controle (ControlPanel) e Modal de Seleção de Eixo (SelectAxleModal).
"""
import tkinter as tk
from typing import List, Dict, Any

from app.config.settings import COLORS
from app.components.alignment_header import AlignmentHeader
from app.components.measurement_card import MeasurementCard
from app.components.tolerance_card import ToleranceCard
from app.components.alignment_indicator import AlignmentIndicator
from app.components.control_panel import ControlPanel
from app.components.select_axle_modal import SelectAxleModal
from app.services.sensor_service import SensorService
from app.utils.scroll_helper import setup_canvas_scrolling

class TrucksMedidasView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#1c2230")
        self.router = router
        self.kwargs = kwargs or {}

        # Estado da Medição
        self.active_tab = "inicial" # "inicial" ou "final"
        self.rim_size = 22
        self.is_manual_override = False # Permite edição manual mesmo com sensor ligado

        # Serviço de Sensores DKA
        self.sensor_service = SensorService.get_instance()
        self.sensor_service.start_server()
        self.sensor_service.add_listener(self._on_sensor_data)

        # Referências aos cartões ativos para atualização direta sem reconstruir todo o DOM
        self.active_cards = {}

        # Lista de Eixos da Composição (gerada dinamicamente a partir da tela de configuração anterior)
        self.axles_list = self._build_axles_from_composition()
        self.active_axle = self.axles_list[0] # Primeiro eixo por padrão

        # Dicionário de armazenamento de medições: {tab: {axle_id: {param: val}}}
        self.measurements_store = {
            "inicial": {
                "D1": {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "conv_l": 0.75, "conv_tot": 1.50, "conv_r": 0.75, "camb_l": 0.20, "camb_r": 0.25, "cast_l": 2.50, "cast_r": 2.50, "kpi_l": 5.10, "kpi_r": 5.10},
                "T1": {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "dist": 3.20, "angle": 0.05, "camb_l": 0.10, "camb_r": 0.10, "conv_l": 0.50, "conv_tot": 1.00, "conv_r": 0.50}
            },
            "final": {
                "D1": {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "conv_l": 0.65, "conv_tot": 1.30, "conv_r": 0.65, "camb_l": 0.15, "camb_r": 0.15, "cast_l": 2.60, "cast_r": 2.60, "kpi_l": 5.00, "kpi_r": 5.00},
                "T1": {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "dist": 3.20, "angle": 0.00, "camb_l": 0.05, "camb_r": 0.05, "conv_l": 0.40, "conv_tot": 0.80, "conv_r": 0.40}
            }
        }

        self._build_ui()
        self._update_mode_ui_and_cards()

    def _build_axles_from_composition(self) -> List[Dict[str, Any]]:
        units = (
            self.kwargs.get("composition_units") or
            self.kwargs.get("units_data") or
            [{"type": "Cavalo Mecânico", "front_axles": 1, "rear_axles": 2}]
        )

        axles = []
        d_count = 1
        t_count = 1
        c_count = 1

        for u in units:
            u_type = u.get("type", "Cavalo Mecânico")
            is_trailer = u_type in ["Semirreboque", "Reboque", "Dolly", "Implemento"]
            f_axles = u.get("front_axles", 0 if is_trailer else 1)
            r_axles = u.get("rear_axles", 2 if not is_trailer else 3)

            # Eixos Dianteiros (Direcionais)
            for _ in range(f_axles):
                axles.append({
                    "id": f"D{d_count}",
                    "name": f"Dianteiro {d_count}",
                    "is_steering": True,
                    "unit_type": u_type
                })
                d_count += 1

            # Eixos Traseiros (Tração ou Carreta)
            for _ in range(r_axles):
                if is_trailer:
                    axles.append({
                        "id": f"C{c_count}",
                        "name": f"Carreta {c_count}",
                        "is_steering": False,
                        "unit_type": u_type
                    })
                    c_count += 1
                else:
                    axles.append({
                        "id": f"T{t_count}",
                        "name": f"Traseiro {t_count} (Tração)",
                        "is_steering": False,
                        "unit_type": u_type
                    })
                    t_count += 1

        if not axles:
            axles = [
                {"id": "D1", "name": "Dianteiro 1", "is_steering": True},
                {"id": "T1", "name": "Traseiro 1 (Tração)", "is_steering": False}
            ]

        return axles

    def _is_sensor_connected(self) -> bool:
        if not hasattr(self, "sensor_service"):
            return False
        import time
        now = time.time()
        for pos_id, last_upd in self.sensor_service.last_updates.items():
            if last_upd > 0 and (now - last_upd) < 5.0:
                h = self.sensor_service.heads_data.get(pos_id)
                if h and h.get("conectado", True):
                    return True
        return False

    def _get_alignment_mode(self) -> str:
        if not self._is_sensor_connected():
            return "MANUAL"
        if self.is_manual_override:
            return "SENSOR_OVERRIDE"
        return "SENSOR"

    def _toggle_manual_override(self) -> bool:
        self.is_manual_override = not self.is_manual_override
        self._update_mode_ui_and_cards()
        return self.is_manual_override

    def _update_mode_ui_and_cards(self):
        mode = self._get_alignment_mode()
        is_read_only = (mode == "SENSOR")

        if mode == "MANUAL":
            self.lbl_mode_badge.config(
                text="🖐️ Modo Manual (Sensores Não Conectados)",
                fg="#f59e0b"
            )
        elif mode == "SENSOR_OVERRIDE":
            self.lbl_mode_badge.config(
                text="✏️ SENSOR LIGADO — EDIÇÃO MANUAL ATIVADA",
                fg="#38bdf8"
            )
        else: # SENSOR
            self.lbl_mode_badge.config(
                text="📡 Modo Sensor (Leitura Automática)",
                fg="#10b981"
            )

        for card in self.active_cards.values():
            if hasattr(card, "set_read_only"):
                card.set_read_only(is_read_only)

    def _on_advance_next(self):
        mode = self._get_alignment_mode()
        self.router.navigate(
            "trucks.finalizar",
            store=self.measurements_store,
            units_data=self.kwargs.get("units_data"),
            alignment_mode=mode
        )

    def _get_active_data(self) -> Dict[str, float]:
        tab_data = self.measurements_store.setdefault(self.active_tab, {})
        axle_id = self.active_axle["id"]
        if axle_id not in tab_data:
            if self.active_axle["is_steering"]:
                tab_data[axle_id] = {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "conv_l": 0.75, "conv_tot": 1.50, "conv_r": 0.75, "camb_l": 0.20, "camb_r": 0.25, "cast_l": 2.50, "cast_r": 2.50, "kpi_l": 5.10, "kpi_r": 5.10}
            else:
                tab_data[axle_id] = {"rf_l": 0.0, "rf_tot": 0.0, "rf_r": 0.0, "dist": 3.20, "angle": 0.05, "camb_l": 0.10, "camb_r": 0.10, "conv_l": 0.50, "conv_tot": 1.00, "conv_r": 0.50}
        return tab_data[axle_id]

    def _build_ui(self):
        # ==========================================
        # 1. CABEÇALHO TÉCNICO (AlignmentHeader)
        # ==========================================
        self.header = AlignmentHeader(
            self,
            title="Medição Física",
            subtitle=f"VOLVO FH 540  •  Conjunto com {len(self.axles_list)} Eixos  ({self.active_axle['name']})",
            on_back=lambda: self.router.navigate("trucks.setup"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # ==========================================
        # 2. BARRA DE ABAS DE ESTADO (Inicial vs Final)
        # ==========================================
        self.tabs_bar = tk.Frame(self, bg="#111520", highlightbackground="#2a3245", highlightthickness=1, padx=24, pady=10)
        self.tabs_bar.pack(fill="x", side="top")

        self.btn_tab_inicial = tk.Button(
            self.tabs_bar,
            text="  MEDIÇÃO INICIAL (Antes)  ",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_tab("inicial")
        )
        self.btn_tab_inicial.pack(side="left", padx=(0, 12))

        self.btn_tab_final = tk.Button(
            self.tabs_bar,
            text="  MEDIÇÃO FINAL (Depois)  ",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg="#1a1f2e",
            activebackground="#059669",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_tab("final")
        )
        self.btn_tab_final.pack(side="left")

        # Badge de Aviso Amarelo à Direita
        self.lbl_mode_badge = tk.Label(
            self.tabs_bar,
            text="⚠️ Modo Medição Inicial (Antes do Ajuste)",
            font=("Segoe UI", 9, "bold"),
            fg="#f59e0b",
            bg="#1c2230",
            padx=12,
            pady=4
        )
        self.lbl_mode_badge.pack(side="right")

        # ==========================================
        # 3. CONTAINER PRINCIPAL: GRADE DE MEDIÇÃO + PAINEL DE CONTROLE
        # ==========================================
        self.body = tk.Frame(self, bg="#1c2230")
        self.body.pack(fill="both", expand=True)

        # ------------------------------------------
        # ÁREA CENTRAL DE LANÇAMENTO (GRID 3 COLUNAS)
        # ------------------------------------------
        self.grid_scroll_container = tk.Frame(self.body, bg="#1c2230")
        self.grid_scroll_container.pack(side="left", fill="both", expand=True)

        self.grid_canvas = tk.Canvas(self.grid_scroll_container, bg="#1c2230", highlightthickness=0, bd=0)
        self.grid_canvas.pack(fill="both", expand=True, padx=24, pady=20)

        self.grid_inner = tk.Frame(self.grid_canvas, bg="#1c2230")
        self.grid_canvas.create_window((0, 0), window=self.grid_inner, anchor="nw")

        self.grid_canvas.bind("<Configure>", lambda e: self.grid_canvas.itemconfig(self.grid_canvas.find_withtag("all")[0], width=e.width))
        setup_canvas_scrolling(self.grid_canvas, self.grid_inner)

        self.grid_inner.grid_columnconfigure(0, weight=1)
        self.grid_inner.grid_columnconfigure(1, weight=1)
        self.grid_inner.grid_columnconfigure(2, weight=1)

        # ------------------------------------------
        # PAINEL LATERAL FIXO DE CONTROLE
        # ------------------------------------------
        self.control_panel = ControlPanel(
            self.body,
            active_axle_name=self.active_axle["name"],
            rim_size=self.rim_size,
            on_change_rim=self._on_change_rim,
            on_open_axle_modal=self._open_axle_modal,
            on_back_initial=lambda: self.router.navigate("trucks.setup"),
            on_advance=self._on_advance_next,
            on_toggle_override=self._toggle_manual_override
        )
        self.control_panel.pack(side="right", fill="y")

        # Renderizar a grade de medição inicial
        self._render_measurement_grid()

    def _switch_tab(self, tab_name: str):
        self.active_tab = tab_name
        if tab_name == "inicial":
            self.btn_tab_inicial.config(bg="#2563eb")
            self.btn_tab_final.config(bg="#1a1f2e")
            self.lbl_mode_badge.config(text="⚠️ Modo Medição Inicial (Antes do Ajuste)", fg="#f59e0b")
        else:
            self.btn_tab_inicial.config(bg="#1a1f2e")
            self.btn_tab_final.config(bg="#059669")
            self.lbl_mode_badge.config(text="✓ Modo Medição Final (Após o Ajuste)", fg="#10b981")

        self._render_measurement_grid()

    def _on_change_rim(self, new_rim: int):
        self.rim_size = new_rim

    def _open_axle_modal(self):
        SelectAxleModal(
            self,
            axles_list=self.axles_list,
            current_axle_id=self.active_axle["id"],
            on_select=self._on_axle_selected,
            on_close=lambda: None
        )

    def _on_axle_selected(self, new_axle: Dict[str, Any]):
        self.active_axle = new_axle
        self.control_panel.update_active_axle(new_axle["name"])
        self.header.pack_forget()
        self.header = AlignmentHeader(
            self,
            title="Medição Física",
            subtitle=f"VOLVO FH 540  •  Conjunto com {len(self.axles_list)} Eixos  ({new_axle['name']})",
            on_back=lambda: self.router.navigate("trucks.setup"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")
        self.header.lower()
        self._render_measurement_grid()

    def _render_measurement_grid(self):
        for child in self.grid_inner.winfo_children():
            child.destroy()

        self.active_cards.clear()
        data = self._get_active_data()
        is_steering = self.active_axle.get("is_steering", True)
        is_read_only = (self._get_alignment_mode() == "SENSOR")

        if is_steering:
            # ==========================================
            # SEÇÃO A: EIXO DIANTEIRO / DIRECIONAL (5 Linhas)
            # ==========================================

            # Linha 1 (Reta): Reta Frente Esq | Reta Frente Total | Reta Frente Dir
            card = MeasurementCard(self.grid_inner, title="Reta Frente Esq", value=data.get("rf_l", 0.0), on_change=lambda v: data.update({"rf_l": v}))
            card.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_l"] = card

            card = MeasurementCard(self.grid_inner, title="Reta Frente Total", value=data.get("rf_tot", 0.0), on_change=lambda v: data.update({"rf_tot": v}))
            card.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_tot"] = card

            card = MeasurementCard(self.grid_inner, title="Reta Frente Dir", value=data.get("rf_r", 0.0), on_change=lambda v: data.update({"rf_r": v}))
            card.grid(row=0, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_r"] = card

            # Linha 2 (Convergência): Conv Diant Esq | Conv Diant Total | Conv Diant Dir
            card = ToleranceCard(self.grid_inner, title="Conv Diant Esq", value=data.get("conv_l", 0.75), min_tol=0.49, max_tol=1.00, on_change=lambda v: data.update({"conv_l": v}))
            card.grid(row=1, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_l"] = card

            card = ToleranceCard(self.grid_inner, title="Conv Diant Total", value=data.get("conv_tot", 1.50), min_tol=1.00, max_tol=2.00, on_change=lambda v: data.update({"conv_tot": v}))
            card.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_tot"] = card

            card = ToleranceCard(self.grid_inner, title="Conv Diant Dir", value=data.get("conv_r", 0.75), min_tol=0.49, max_tol=1.00, on_change=lambda v: data.update({"conv_r": v}))
            card.grid(row=1, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_r"] = card

            # Linha 3 (Camber): Camber Diant Esq | AlignmentIndicator | Camber Diant Dir
            card = ToleranceCard(self.grid_inner, title="Camber Diant Esq", value=data.get("camb_l", 0.20), min_tol=0.00, max_tol=0.50, unit="°", on_change=lambda v: self._update_camber_l(v, data))
            card.grid(row=2, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["camb_l"] = card

            self.ind_camber = AlignmentIndicator(self.grid_inner, val_left=data.get("camb_l", 0.20), val_right=data.get("camb_r", 0.25), label="CAMBER")
            self.ind_camber.grid(row=2, column=1, sticky="ew", padx=6, pady=6)

            card = ToleranceCard(self.grid_inner, title="Camber Diant Dir", value=data.get("camb_r", 0.25), min_tol=0.00, max_tol=0.50, unit="°", on_change=lambda v: self._update_camber_r(v, data))
            card.grid(row=2, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["camb_r"] = card

            # Linha 4 (Caster): Caster Esq | AlignmentIndicator | Caster Dir
            card = ToleranceCard(self.grid_inner, title="Caster Esq", value=data.get("cast_l", 2.50), min_tol=2.00, max_tol=3.50, unit="°", on_change=lambda v: self._update_caster_l(v, data))
            card.grid(row=3, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["cast_l"] = card

            self.ind_caster = AlignmentIndicator(self.grid_inner, val_left=data.get("cast_l", 2.50), val_right=data.get("cast_r", 2.50), label="CASTER")
            self.ind_caster.grid(row=3, column=1, sticky="ew", padx=6, pady=6)

            card = ToleranceCard(self.grid_inner, title="Caster Dir", value=data.get("cast_r", 2.50), min_tol=2.00, max_tol=3.50, unit="°", on_change=lambda v: self._update_caster_r(v, data))
            card.grid(row=3, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["cast_r"] = card

            # Linha 5 (KPI): KPI Esq | AlignmentIndicator | KPI Dir
            card = ToleranceCard(self.grid_inner, title="KPI Esq", value=data.get("kpi_l", 5.10), min_tol=4.50, max_tol=6.00, unit="°", on_change=lambda v: self._update_kpi_l(v, data))
            card.grid(row=4, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["kpi_l"] = card

            self.ind_kpi = AlignmentIndicator(self.grid_inner, val_left=data.get("kpi_l", 5.10), val_right=data.get("kpi_r", 5.10), label="KPI")
            self.ind_kpi.grid(row=4, column=1, sticky="ew", padx=6, pady=6)

            card = ToleranceCard(self.grid_inner, title="KPI Dir", value=data.get("kpi_r", 5.10), min_tol=4.50, max_tol=6.00, unit="°", on_change=lambda v: self._update_kpi_r(v, data))
            card.grid(row=4, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["kpi_r"] = card

        else:
            # ==========================================
            # SEÇÃO B: EIXO TRASEIRO / TRAÇÃO / CARRETA (5 Linhas)
            # ==========================================

            # Linha 1 (Reta): Reta Frente Esq | Reta Frente Total | Reta Frente Dir
            card = MeasurementCard(self.grid_inner, title="Reta Frente Esq", value=data.get("rf_l", 0.0), on_change=lambda v: data.update({"rf_l": v}))
            card.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_l"] = card

            card = MeasurementCard(self.grid_inner, title="Reta Frente Total", value=data.get("rf_tot", 0.0), on_change=lambda v: data.update({"rf_tot": v}))
            card.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_tot"] = card

            card = MeasurementCard(self.grid_inner, title="Reta Frente Dir", value=data.get("rf_r", 0.0), on_change=lambda v: data.update({"rf_r": v}))
            card.grid(row=0, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["rf_r"] = card

            # Linha 2 (Geometria do Chassis): Espaço Vazio | Distância Entre Eixos | Espaço Vazio
            tk.Label(self.grid_inner, bg="#1c2230").grid(row=1, column=0)
            card = MeasurementCard(self.grid_inner, title="Distância Entre Eixos", value=data.get("dist", 3.20), unit="m", step=0.05, on_change=lambda v: data.update({"dist": v}))
            card.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["dist"] = card
            tk.Label(self.grid_inner, bg="#1c2230").grid(row=1, column=2)

            # Linha 3 (Vetor de Impulso): Espaço Vazio | Ângulo de Impulso | Espaço Vazio
            tk.Label(self.grid_inner, bg="#1c2230").grid(row=2, column=0)
            card = MeasurementCard(self.grid_inner, title="Ângulo de Impulso", value=data.get("angle", 0.05), unit="°", step=0.01, on_change=lambda v: data.update({"angle": v}))
            card.grid(row=2, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["angle"] = card
            tk.Label(self.grid_inner, bg="#1c2230").grid(row=2, column=2)

            # Linha 4 (Camber Traseiro): Camber Tras Esq | AlignmentIndicator | Camber Tras Dir
            card = ToleranceCard(self.grid_inner, title="Camber Tras Esq", value=data.get("camb_l", 0.10), min_tol=0.00, max_tol=0.30, unit="°", on_change=lambda v: self._update_camber_l(v, data))
            card.grid(row=3, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["camb_l"] = card

            self.ind_camber = AlignmentIndicator(self.grid_inner, val_left=data.get("camb_l", 0.10), val_right=data.get("camb_r", 0.10), label="CAMBER")
            self.ind_camber.grid(row=3, column=1, sticky="ew", padx=6, pady=6)

            card = ToleranceCard(self.grid_inner, title="Camber Tras Dir", value=data.get("camb_r", 0.10), min_tol=0.00, max_tol=0.30, unit="°", on_change=lambda v: self._update_camber_r(v, data))
            card.grid(row=3, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["camb_r"] = card

            # Linha 5 (Convergência Traseira): Conv Tras Esq | Conv Tras Total | Conv Tras Dir
            card = ToleranceCard(self.grid_inner, title="Conv Tras Esq", value=data.get("conv_l", 0.50), min_tol=0.20, max_tol=0.80, on_change=lambda v: data.update({"conv_l": v}))
            card.grid(row=4, column=0, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_l"] = card

            card = ToleranceCard(self.grid_inner, title="Conv Tras Total", value=data.get("conv_tot", 1.00), min_tol=0.40, max_tol=1.60, on_change=lambda v: data.update({"conv_tot": v}))
            card.grid(row=4, column=1, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_tot"] = card

            card = ToleranceCard(self.grid_inner, title="Conv Tras Dir", value=data.get("conv_r", 0.50), min_tol=0.20, max_tol=0.80, on_change=lambda v: data.update({"conv_r": v}))
            card.grid(row=4, column=2, sticky="ew", padx=6, pady=6)
            self.active_cards["conv_r"] = card

        # Atualizar a região de rolagem da grade
        self.grid_inner.update_idletasks()
        self.grid_canvas.config(scrollregion=(0, 0, self.grid_inner.winfo_width(), self.grid_inner.winfo_height()))

    def _toggle_simulation(self) -> bool:
        # return self.sensor_service.toggle_simulation()
        return False

    def _on_sensor_data(self, pos_id: int, data: Dict[str, Any]):
        """Callback executado em thread secundária ao receber dados do sensor."""
        self.after(0, lambda: self._process_sensor_data(pos_id, data))

    def _process_sensor_data(self, pos_id: int, data: Dict[str, Any]):
        is_connected = data.get("conectado", True)
        batt = data.get("batt", 0)

        # 1. Atualizar indicador no painel lateral e estado de modo
        self.control_panel.update_sensor_head(pos_id, is_connected, batt)
        self._update_mode_ui_and_cards()

        if not is_connected:
            return

        # Se em Modo Sensor Automático (sem sobrescrição manual), atualizar valores dos sensores
        if self._get_alignment_mode() == "SENSOR":
            active_data = self._get_active_data()
            is_steering = self.active_axle.get("is_steering", True)

            if is_steering:
                if pos_id == 0:  # DM
                    if "conv" in data:   active_data["conv_l"] = data["conv"]
                    if "camber" in data: active_data["camb_l"] = data["camber"]
                    if "caster" in data: active_data["cast_l"] = data["caster"]
                    if "kpi" in data:    active_data["kpi_l"]  = data["kpi"]
                elif pos_id == 1:  # DP
                    if "conv" in data:   active_data["conv_r"] = data["conv"]
                    if "camber" in data: active_data["camb_r"] = data["camber"]
                    if "caster" in data: active_data["cast_r"] = data["caster"]
                    if "kpi" in data:    active_data["kpi_r"]  = data["kpi"]

                active_data["conv_tot"] = round(active_data.get("conv_l", 0.0) + active_data.get("conv_r", 0.0), 2)
            else:
                if pos_id == 2:  # TM
                    if "conv" in data:   active_data["conv_l"] = data["conv"]
                    if "camber" in data: active_data["camb_l"] = data["camber"]
                elif pos_id == 3:  # TP
                    if "conv" in data:   active_data["conv_r"] = data["conv"]
                    if "camber" in data: active_data["camb_r"] = data["camber"]

                active_data["conv_tot"] = round(active_data.get("conv_l", 0.0) + active_data.get("conv_r", 0.0), 2)

            # 2. Atualizar cartões visuais diretamente
            for key, card in self.active_cards.items():
                if key in active_data:
                    card.update_value(active_data[key])

            # 3. Atualizar indicadores de inclinação visual de pneus
            if hasattr(self, "ind_camber"):
                self.ind_camber.update_angles(active_data.get("camb_l", 0.0), active_data.get("camb_r", 0.0))
            if hasattr(self, "ind_caster"):
                self.ind_caster.update_angles(active_data.get("cast_l", 0.0), active_data.get("cast_r", 0.0))
            if hasattr(self, "ind_kpi"):
                self.ind_kpi.update_angles(active_data.get("kpi_l", 0.0), active_data.get("kpi_r", 0.0))

    def destroy(self):
        if hasattr(self, "sensor_service"):
            self.sensor_service.remove_listener(self._on_sensor_data)
        super().destroy()

    def _update_camber_l(self, val: float, data: dict):
        data["camb_l"] = val
        if hasattr(self, "ind_camber"):
            self.ind_camber.update_angles(val, data.get("camb_r", 0.0))

    def _update_camber_r(self, val: float, data: dict):
        data["camb_r"] = val
        if hasattr(self, "ind_camber"):
            self.ind_camber.update_angles(data.get("camb_l", 0.0), val)

    def _update_caster_l(self, val: float, data: dict):
        data["cast_l"] = val
        if hasattr(self, "ind_caster"):
            self.ind_caster.update_angles(val, data.get("cast_r", 0.0))

    def _update_caster_r(self, val: float, data: dict):
        data["cast_r"] = val
        if hasattr(self, "ind_caster"):
            self.ind_caster.update_angles(data.get("cast_l", 0.0), val)

    def _update_kpi_l(self, val: float, data: dict):
        data["kpi_l"] = val
        if hasattr(self, "ind_kpi"):
            self.ind_kpi.update_angles(val, data.get("kpi_r", 0.0))

    def _update_kpi_r(self, val: float, data: dict):
        data["kpi_r"] = val
        if hasattr(self, "ind_kpi"):
            self.ind_kpi.update_angles(data.get("kpi_l", 0.0), val)
