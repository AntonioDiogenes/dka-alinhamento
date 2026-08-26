"""
Visualizador Gráfico Dinâmico do Chassis e Eixos em Tempo Real (components/truck_chassis_preview.py).
Renderiza o desenho vetorial de alta precisão do chassis, viga central, eixos dianteiros (roda simples), tanques de combustível e eixos traseiros (rodado duplo), além do pino rei / quinta roda amarela entre unidades acopladas.
Possui suporte completo a Rolagem/Overflow vertical (Scrollbar + MouseWheel).
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

class TruckChassisPreview(tk.Frame):
    def __init__(self, parent: tk.Widget, units_data: List[Dict[str, Any]], **kwargs):
        super().__init__(parent, bg="#0d1117", **kwargs)
        self.units_data = units_data

        # Container interno para o Canvas e a Scrollbar de Overflow
        self.scrollbar = ttk.Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self, bg="#0d1117", highlightthickness=0, bd=0, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        self.scrollbar.config(command=self.canvas.yview)

        # Eventos de Rolagem por Scroll do Mouse / Touchpad
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.canvas.bind("<Configure>", lambda e: self.draw_chassis())

        self.draw_chassis()

    def _bind_mousewheel(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def update_composition(self, units_data: List[Dict[str, Any]]):
        self.units_data = units_data
        self.draw_chassis()

    def draw_chassis(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        c_width = max(self.canvas.winfo_width(), 450)
        center_x = c_width // 2
        curr_y = 40

        for idx, unit in enumerate(self.units_data):
            unit_type = unit.get("type", "Cavalo Mecânico")
            front_axles = unit.get("front_axles", 1)
            rear_axles = unit.get("rear_axles", 2)
            total_axles = unit.get("total_axles", 3)

            # Se for reboque/semirreboque que usa apenas contador único
            is_trailer = unit_type in ["Semirreboque", "Reboque", "Dolly", "Implemento"]
            if is_trailer:
                front_axles = 0
                rear_axles = total_axles

            # Calcular altura dinâmica da viga central
            rail_height = 200 + (rear_axles * 70) + (front_axles * 50)
            rail_width = 56
            rail_left = center_x - (rail_width // 2)
            rail_right = center_x + (rail_width // 2)

            # Rótulo de Identificação da Unidade (ex: CAVALO MECÂNICO #1)
            self.canvas.create_text(
                center_x,
                curr_y,
                text=f"UNIT {idx+1}: {unit_type.upper()}",
                fill="#60a5fa",
                font=("Segoe UI", 9, "bold")
            )
            curr_y += 24

            # 1. Viga Longarina Central (#262626 / neutral-800)
            rail_top_y = curr_y
            rail_bot_y = curr_y + rail_height
            self.canvas.create_rectangle(
                rail_left, rail_top_y, rail_right, rail_bot_y,
                fill="#262626", outline="#404040", width=2
            )

            axle_y = rail_top_y + 40

            # 2. SEÇÃO 1: EIXOS DIANTEIROS (Rodado Simples / Direcionais)
            for f in range(front_axles):
                # Roda Simples Esquerda (w=22, h=54)
                w_left_x1 = rail_left - 36
                w_left_x2 = rail_left - 14
                self.canvas.create_rectangle(
                    w_left_x1, axle_y - 27, w_left_x2, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )
                # Barra de Eixo Esquerda
                self.canvas.create_rectangle(
                    w_left_x2, axle_y - 6, rail_left, axle_y + 6,
                    fill="#404040", outline=""
                )

                # Barra de Eixo Direita
                self.canvas.create_rectangle(
                    rail_right, axle_y - 6, rail_right + 22, axle_y + 6,
                    fill="#404040", outline=""
                )
                # Roda Simples Direita
                w_right_x1 = rail_right + 22
                w_right_x2 = rail_right + 44
                self.canvas.create_rectangle(
                    w_right_x1, axle_y - 27, w_right_x2, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )

                axle_y += 54

            # 3. SEÇÃO 2: TANQUES DE COMBUSTÍVEL LATERAIS (Side Blocks)
            tank_y = axle_y + 10
            tank_w = 40
            tank_h = 75

            # Tanque Esquerdo
            self.canvas.create_rectangle(
                rail_left - tank_w - 8, tank_y, rail_left - 8, tank_y + tank_h,
                fill="#737373", outline="#a3a3a3", width=1.5
            )
            # Fitas metálicas do tanque esquerdo
            self.canvas.create_line(rail_left - tank_w - 8, tank_y + 22, rail_left - 8, tank_y + 22, fill="#525252", width=3)
            self.canvas.create_line(rail_left - tank_w - 8, tank_y + 52, rail_left - 8, tank_y + 52, fill="#525252", width=3)

            # Tanque Direito
            self.canvas.create_rectangle(
                rail_right + 8, tank_y, rail_right + tank_w + 8, tank_y + tank_h,
                fill="#737373", outline="#a3a3a3", width=1.5
            )
            # Fitas metálicas do tanque direito
            self.canvas.create_line(rail_right + 8, tank_y + 22, rail_right + tank_w + 8, tank_y + 22, fill="#525252", width=3)
            self.canvas.create_line(rail_right + 8, tank_y + 52, rail_right + tank_w + 8, tank_y + 52, fill="#525252", width=3)

            axle_y = tank_y + tank_h + 36

            # 4. SEÇÃO 3: EIXOS TRASEIROS (Tração / Rodados Duplos)
            for r in range(rear_axles):
                # Rodado Duplo Esquerdo (Duas rodas grudadas)
                self.canvas.create_rectangle(
                    rail_left - 52, axle_y - 27, rail_left - 32, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )
                self.canvas.create_rectangle(
                    rail_left - 30, axle_y - 27, rail_left - 10, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )
                self.canvas.create_rectangle(
                    rail_left - 10, axle_y - 8, rail_left, axle_y + 8,
                    fill="#404040", outline=""
                )

                # Conector de Eixo Direito
                self.canvas.create_rectangle(
                    rail_right, axle_y - 8, rail_right + 10, axle_y + 8,
                    fill="#404040", outline=""
                )
                # Rodado Duplo Direito (Roda interna + Roda externa)
                self.canvas.create_rectangle(
                    rail_right + 10, axle_y - 27, rail_right + 30, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )
                self.canvas.create_rectangle(
                    rail_right + 32, axle_y - 27, rail_right + 52, axle_y + 27,
                    fill="#a3a3a3", outline="#d4d4d4", width=1.5
                )

                axle_y += 64

            curr_y = rail_bot_y + 24

            # 5. CONECTOR MECÂNICO DE QUINTA RODA AMARERO (Entre Unidades)
            if idx < len(self.units_data) - 1:
                self.canvas.create_rectangle(
                    center_x - 6, curr_y, center_x + 6, curr_y + 36,
                    fill="#eab308", outline="#fde047", width=2
                )
                self.canvas.create_text(
                    center_x + 40,
                    curr_y + 18,
                    text="5ª RODA / PINO REI",
                    fill="#eab308",
                    font=("Segoe UI", 7, "bold")
                )
                curr_y += 50

        # Atualizar a região de rolagem (Overflow Scroll Region)
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=(0, 0, max(c_width, bbox[2]), bbox[3] + 40))
        else:
            self.canvas.config(scrollregion=(0, 0, c_width, curr_y + 40))
