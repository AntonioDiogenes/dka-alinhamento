"""
Componente NavCard para a grade de rotinas operacionais na tela principal.
Suporta layout flexível, bordas arredondadas, hover em azul elétrico (#4f77ff) e micro-animação de clique.
"""
import tkinter as tk
from typing import Callable, Optional
from app.config.settings import COLORS, FONTS
from app.utils.icons import create_icon_image

class NavCard(tk.Canvas):
    """
    Card interativo de navegação rápida com tamanho 180-240px (largura) por 120px (altura).
    """
    def __init__(
        self,
        master: tk.Widget,
        title: str,
        icon_name: str,
        command: Callable[[], None],
        width: int = 210,
        height: int = 120,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=COLORS["bg_dark"],
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.title_text = title
        self.icon_name = icon_name
        self.command = command
        self.card_width = width
        self.card_height = height

        # Estado de animação/hover
        self.is_hovered = False
        self.is_pressed = False

        # Pré-gerar ícones normal e hover
        self.icon_normal = create_icon_image(icon_name, size=46, color="#FFFFFF", stroke_width=1.6)
        self.icon_hover = create_icon_image(icon_name, size=46, color="#FFFFFF", stroke_width=1.8)

        # Bind de eventos interativos
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)

        self._draw_card()

    def _on_configure(self, event):
        if event.width > 10 and event.height > 10:
            self.card_width = event.width
            self.card_height = event.height
            self._draw_card()

    def _draw_card(self):
        self.delete("all")
        w, h = self.card_width, self.card_height

        # Animação de pressão (scale-95): margem interna maior quando pressionado
        if self.is_pressed:
            pad = 6
            bg_color = "#3b5edb"         # Azul elétrico ativo mais profundo
            border_color = "#6085ff"     # Borda brilhante
            icon_img = self.icon_hover
        elif self.is_hovered:
            pad = 2
            bg_color = COLORS["accent_blue"] # #4f77ff
            border_color = "#809fff"
            icon_img = self.icon_hover
        else:
            pad = 2
            bg_color = "#151a26"         # Translúcido escuro
            border_color = "#333d54"     # Borda suave
            icon_img = self.icon_normal

        radius = 12
        x1, y1 = pad, pad
        x2, y2 = w - pad, h - pad

        # Desenhar retângulo arredondado (Background + Border)
        self._create_rounded_rect(x1, y1, x2, y2, radius, fill=bg_color, outline=border_color, width=2)

        # Desenhar Ícone centralizado no topo (y = h * 0.38)
        icon_y = (y1 + y2) * 0.38
        self.create_image(w / 2, icon_y, image=icon_img, anchor="center")

        # Desenhar Título em branco centralizado abaixo do ícone (y = h * 0.76)
        text_y = (y1 + y2) * 0.78
        self.create_text(
            w / 2,
            text_y,
            text=self.title_text,
            fill=COLORS["text_white"],
            font=FONTS["card_title"],
            anchor="center"
        )

    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event):
        self.is_hovered = True
        self._draw_card()

    def _on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self._draw_card()

    def _on_press(self, event):
        self.is_pressed = True
        self._draw_card()

    def _on_release(self, event):
        if self.is_pressed:
            self.is_pressed = False
            self._draw_card()
            if self.command:
                self.command()
