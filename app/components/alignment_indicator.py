"""
Indicador Gráfico de Inclinação de Rodas Responsivo em Tempo Real (components/alignment_indicator.py).
Recursos:
- Redesenho automático no evento <Configure> para adaptação a qualquer tamanho de tela/janela.
- Posicionamento percentual (25% Esquerda e 75% Direita) garantindo que ambas as rodas fiquem 100% visíveis e centralizadas.
- Inclinação física vetorial dinâmica recalculada instantaneamente.
"""
import math
import tkinter as tk

class AlignmentIndicator(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        val_left: float = 0.0,
        val_right: float = 0.0,
        label: str = "INCLINAÇÃO",
        **kwargs
    ):
        super().__init__(
            parent,
            bg="#1a1f2e",
            height=110,
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=8,
            pady=6,
            **kwargs
        )
        self.pack_propagate(False)

        self.val_left = val_left
        self.val_right = val_right
        self.label = label

        self.canvas = tk.Canvas(self, bg="#1a1f2e", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Redesenhar automaticamente sempre que a janela ou o container mudar de tamanho (<Configure>)
        self.canvas.bind("<Configure>", lambda e: self.draw_indicator())

        self.draw_indicator()

    def update_angles(self, val_left: float, val_right: float):
        self.val_left = val_left
        self.val_right = val_right
        self.draw_indicator()

    def draw_indicator(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 50 or h < 30:
            return

        # Posições responsivas percentuais (25% para Roda Esquerda, 75% para Roda Direita)
        x_left = int(w * 0.25)
        x_right = int(w * 0.75)
        x_center = w // 2

        # 1. Rótulos de Cabeçalho (ESQ | NOME | DIR)
        self.canvas.create_text(x_left, 10, text="ESQ", fill="#9ca3af", font=("Segoe UI", 8, "bold"))
        self.canvas.create_text(x_center, 10, text=self.label.upper(), fill="#60a5fa", font=("Segoe UI", 8, "bold"))
        self.canvas.create_text(x_right, 10, text="DIR", fill="#9ca3af", font=("Segoe UI", 8, "bold"))

        # 2. Linha de Solo e Eixo Central Tracejado
        self.canvas.create_line(12, h - 12, w - 12, h - 12, fill="#404040", width=2)
        self.canvas.create_line(x_center, 22, x_center, h - 12, fill="#3b4252", dash=(4, 4))

        # 3. Roda Esquerda (Tilt: Angle = val_left * 12.0, max 35)
        angle_l = max(-35.0, min(35.0, self.val_left * 12.0))
        self._draw_tilted_wheel(x_center=x_left, y_center=(h // 2) + 4, angle_deg=angle_l, val=self.val_left)

        # 4. Roda Direita (Tilt: Angle = val_right * 12.0, max 35)
        angle_r = max(-35.0, min(35.0, self.val_right * 12.0))
        self._draw_tilted_wheel(x_center=x_right, y_center=(h // 2) + 4, angle_deg=angle_r, val=self.val_right)

    def _draw_tilted_wheel(self, x_center: float, y_center: float, angle_deg: float, val: float):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Polígono de Roda Retangular (w=18, h=38)
        hw, hh = 9.0, 19.0
        corners = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
        ]

        rotated_pts = []
        for dx, dy in corners:
            rx = dx * cos_a - dy * sin_a + x_center
            ry = dx * sin_a + dy * cos_a + y_center
            rotated_pts.extend([rx, ry])

        # Pneu com borda azul destacada
        self.canvas.create_polygon(rotated_pts, fill="#525252", outline="#60a5fa", width=1.5)

        # Texto com o valor em graus/mm acima da roda
        val_str = f"{'+' if val >= 0 else ''}{val:.2f}°" if "°" not in str(val) else f"{'+' if val >= 0 else ''}{val:.2f}"
        self.canvas.create_text(x_center, y_center - 26, text=val_str, fill="#ffffff", font=("Segoe UI", 8, "bold"))

        # Seta indicadora de direção de inclinação
        arrow_y = y_center - 14
        arrow_x = x_center + (sin_a * 14)
        self.canvas.create_line(x_center, y_center, arrow_x, arrow_y, fill="#60a5fa", width=2, arrow=tk.FIRST)
