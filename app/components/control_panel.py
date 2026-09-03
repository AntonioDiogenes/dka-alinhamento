"""
Painel Lateral Fixo de Controle (components/control_panel.py).
Posicionado na lateral direita da tela de Medição Física (largura 320px).
Contém:
1. Ajuste de Aro da Roda (13" a 30").
2. Identificador de Eixo Ativo (ex: Dianteiro 1, Traseiro 2).
3. Botoeira de Navegação (Iniciais, Trocar Eixo, Avançar ->).
"""
import tkinter as tk
from typing import Callable, Optional

from app.utils.icons import create_icon_image

class ControlPanel(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        active_axle_name: str = "Dianteiro 1",
        rim_size: int = 22,
        on_change_rim: Optional[Callable[[int], None]] = None,
        on_open_axle_modal: Optional[Callable[[], None]] = None,
        on_back_initial: Optional[Callable[[], None]] = None,
        on_advance: Optional[Callable[[], None]] = None,
        on_toggle_simulation: Optional[Callable[[], bool]] = None,
        on_toggle_override: Optional[Callable[[], bool]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            bg="#272f43",
            width=320,
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=20,
            pady=24,
            **kwargs
        )
        self.pack_propagate(False)

        self.active_axle_name = active_axle_name
        self.rim_size = rim_size
        self.on_change_rim = on_change_rim
        self.on_open_axle_modal = on_open_axle_modal
        self.on_back_initial = on_back_initial
        self.on_advance = on_advance
        self.on_toggle_simulation = on_toggle_simulation
        self.on_toggle_override = on_toggle_override
        self.is_manual_override = False

        # Ícones
        self.img_back = create_icon_image("chevron_left", size=18, color="#FFFFFF")
        self.img_next = create_icon_image("chevron_right", size=18, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # 1. AJUSTE DE ARO DA RODA (13" a 30")
        rim_box = tk.Frame(self, bg="#1a1f2e", highlightbackground="#2a3245", highlightthickness=1, padx=16, pady=16)
        rim_box.pack(fill="x", pady=(0, 24))

        lbl_rim_title = tk.Label(rim_box, text="TAMANHO DO ARO DA RODA", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e")
        lbl_rim_title.pack(anchor="w")

        rim_ctrl = tk.Frame(rim_box, bg="#1a1f2e")
        rim_ctrl.pack(fill="x", pady=(8, 0))

        btn_rim_minus = tk.Button(
            rim_ctrl,
            text="-",
            font=("Segoe UI", 14, "bold"),
            fg="#60a5fa",
            bg="#0d1117",
            activebackground="#2563eb",
            activeforeground="white",
            bd=1,
            highlightbackground="#2563eb",
            width=3,
            cursor="hand2",
            command=self._dec_rim
        )
        btn_rim_minus.pack(side="left")

        self.lbl_rim_val = tk.Label(
            rim_ctrl,
            text=f'Aro: {self.rim_size}"',
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF",
            bg="#1a1f2e"
        )
        self.lbl_rim_val.pack(side="left", expand=True)

        btn_rim_plus = tk.Button(
            rim_ctrl,
            text="+",
            font=("Segoe UI", 14, "bold"),
            fg="#60a5fa",
            bg="#0d1117",
            activebackground="#2563eb",
            activeforeground="white",
            bd=1,
            highlightbackground="#2563eb",
            width=3,
            cursor="hand2",
            command=self._inc_rim
        )
        btn_rim_plus.pack(side="right")

        # 2. IDENTIFICADOR DE EIXO ATIVO
        axle_box = tk.Frame(self, bg="#1a1f2e", highlightbackground="#2563eb", highlightthickness=1, padx=16, pady=18)
        axle_box.pack(fill="x", pady=(0, 24))

        lbl_axle_tag = tk.Label(axle_box, text="EIXO EM MEDIÇÃO ATIVO", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e")
        lbl_axle_tag.pack(anchor="w")

        self.lbl_axle_name = tk.Label(
            axle_box,
            text=self.active_axle_name,
            font=("Segoe UI", 18, "bold"),
            fg="#60a5fa",
            bg="#1a1f2e"
        )
        self.lbl_axle_name.pack(anchor="w", pady=(4, 0))

        # 2.5 STATUS DOS SENSORES DKA (TCP 5000)
        sensor_box = tk.Frame(self, bg="#1a1f2e", highlightbackground="#334155", highlightthickness=1, padx=12, pady=12)
        sensor_box.pack(fill="x", pady=(0, 16))

        hdr_s = tk.Frame(sensor_box, bg="#1a1f2e")
        hdr_s.pack(fill="x", pady=(0, 6))

        lbl_sensor_title = tk.Label(hdr_s, text="CABEÇOTES DKA (TCP 5000)", font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#1a1f2e")
        lbl_sensor_title.pack(side="left")

        # self.btn_toggle_sim = tk.Button(
        #     hdr_s,
        #     text="SIMULAR",
        #     font=("Segoe UI", 7, "bold"),
        #     fg="#f59e0b",
        #     bg="#2a3245",
        #     activebackground="#f59e0b",
        #     activeforeground="black",
        #     bd=0,
        #     padx=6,
        #     pady=1,
        #     cursor="hand2",
        #     command=self._handle_toggle_sim
        # )
        # self.btn_toggle_sim.pack(side="right")

        # Grade 2x2 dos 4 cabeçotes (DM, DP, TM, TP)
        grid_s = tk.Frame(sensor_box, bg="#1a1f2e")
        grid_s.pack(fill="x")

        self.head_widgets = {}
        heads_layout = [(0, "DM", 0, 0), (1, "DP", 0, 1), (2, "TM", 1, 0), (3, "TP", 1, 1)]

        for pos_id, name, r, c in heads_layout:
            cell = tk.Frame(grid_s, bg="#111520", padx=6, pady=4, highlightbackground="#2a3245", highlightthickness=1)
            cell.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
            grid_s.columnconfigure(c, weight=1)

            lbl_led = tk.Label(cell, text="●", font=("Segoe UI", 10, "bold"), fg="#6b7280", bg="#111520")
            lbl_led.pack(side="left")

            lbl_name = tk.Label(cell, text=name, font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#111520")
            lbl_name.pack(side="left", padx=2)

            lbl_batt = tk.Label(cell, text="--%", font=("Segoe UI", 8), fg="#9ca3af", bg="#111520")
            lbl_batt.pack(side="right")

            self.head_widgets[pos_id] = {
                "led": lbl_led,
                "name": lbl_name,
                "batt": lbl_batt,
                "cell": cell
            }

        # Botão de Opção: Permitir Edição Manual mesmo com sensor conectado
        self.btn_toggle_override = tk.Button(
            sensor_box,
            text="✏️ Habilitar Edição Manual",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#2a3245",
            activebackground="#0284c7",
            activeforeground="white",
            bd=1,
            relief="solid",
            highlightbackground="#3b82f6",
            pady=6,
            cursor="hand2",
            command=self._handle_toggle_override
        )
        self.btn_toggle_override.pack(fill="x", pady=(10, 0))

        # 3. BOTOEIRA DE NAVEGAÇÃO INFERIOR
        bot_nav = tk.Frame(self, bg="#272f43")
        bot_nav.pack(fill="x", side="bottom", pady=(16, 0))

        # Botão Trocar Eixo
        self.btn_switch_axle = tk.Button(
            bot_nav,
            text=f"Trocar Eixo ({self.active_axle_name})",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            pady=10,
            cursor="hand2",
            command=self._handle_open_modal
        )
        self.btn_switch_axle.pack(fill="x", pady=(0, 12))

        # Linha com Botão Iniciais (<-) e Avançar (->)
        h_nav = tk.Frame(bot_nav, bg="#272f43")
        h_nav.pack(fill="x")

        btn_back_init = tk.Button(
            h_nav,
            text=" Configuração",
            image=self.img_back,
            compound="left",
            font=("Segoe UI", 9, "bold"),
            fg="#9ca3af",
            bg="#1a1f2e",
            activebackground="#2a3245",
            bd=0,
            padx=10,
            pady=8,
            cursor="hand2",
            command=self._handle_back
        )
        btn_back_init.pack(side="left")

        btn_adv = tk.Button(
            h_nav,
            text="Avançar ",
            image=self.img_next,
            compound="right",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#10b981",
            activebackground="#059669",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._handle_advance
        )
        btn_adv.pack(side="right")

    def update_active_axle(self, axle_name: str):
        self.active_axle_name = axle_name
        self.lbl_axle_name.config(text=axle_name)
        self.btn_switch_axle.config(text=f"Trocar Eixo ({axle_name})")

    def _dec_rim(self):
        if self.rim_size > 13:
            self.rim_size -= 1
            self.lbl_rim_val.config(text=f'Aro: {self.rim_size}"')
            if self.on_change_rim:
                self.on_change_rim(self.rim_size)

    def _inc_rim(self):
        if self.rim_size < 30:
            self.rim_size += 1
            self.lbl_rim_val.config(text=f'Aro: {self.rim_size}"')
            if self.on_change_rim:
                self.on_change_rim(self.rim_size)

    def _handle_toggle_override(self):
        if self.on_toggle_override:
            self.is_manual_override = self.on_toggle_override()
            self.update_override_button(self.is_manual_override)

    def update_override_button(self, is_override: bool):
        self.is_manual_override = is_override
        if is_override:
            self.btn_toggle_override.config(
                text="🔓 Sobrescrição Manual: ATIVADA",
                bg="#0284c7",
                activebackground="#0369a1"
            )
        else:
            self.btn_toggle_override.config(
                text="✏️ Habilitar Edição Manual",
                bg="#2a3245",
                activebackground="#0284c7"
            )

    def _handle_toggle_sim(self):
        pass

    def update_sensor_head(self, pos_id: int, is_connected: bool, batt_percent: int):
        if pos_id in self.head_widgets:
            w = self.head_widgets[pos_id]
            if is_connected:
                w["led"].config(fg="#10b981")
                w["batt"].config(text=f"{batt_percent}%", fg="#10b981" if batt_percent > 20 else "#ef4444")
            else:
                w["led"].config(fg="#6b7280")
                w["batt"].config(text="--%", fg="#9ca3af")

    def _handle_open_modal(self):
        if self.on_open_axle_modal:
            self.on_open_axle_modal()

    def _handle_back(self):
        if self.on_back_initial:
            self.on_back_initial()

    def _handle_advance(self):
        if self.on_advance:
            self.on_advance()
