"""
Tela Principal (Dashboard) da Aplicação Desktop.
Layout limpo sem artefatos visuais de duplicação, com suporte a fundo escuro imersivo (#111520),
opção de imagem personalizada, ações (Configurações e Logout), relógio digital gigante (24h) e NavCards.
"""
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

from app.config.settings import COLORS, FONTS, state
from app.config.user_settings import save_user_settings
from app.components.nav_card import NavCard
from app.utils.icons import create_icon_image, pil_to_photoimage

class DashboardView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.router = router

        # Variáveis de Estado da View
        self.clock_after_id = None
        self.bg_photo = None
        self.bg_image_id = None

        # 1. Canvas para suporte a Imagem de Fundo Personalizada (Fundo)
        self.canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # 2. Relógio Digital como texto transparente diretamente sobre o Canvas (sem caixa preta)
        self.clock_text_id = self.canvas.create_text(
            1200, 95,
            text="00:00",
            font=FONTS["title_clock"],
            fill=COLORS["text_white"],
            anchor="ne"
        )

        # 3. Botão Configurações Flutuante Direto no Canvas
        self.btn_settings = tk.Button(
            self.canvas,
            text="Configurações",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_white"],
            bg=COLORS["bg_card"],
            activebackground=COLORS["accent_blue"],
            activeforeground="white",
            bd=1,
            relief="solid",
            highlightbackground=COLORS["border_subtle"],
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._show_settings_menu
        )
        self.btn_settings_window = self.canvas.create_window(1080, 24, window=self.btn_settings, anchor="ne")

        # 4. Botão Sair Flutuante Direto no Canvas
        self.btn_logout = tk.Button(
            self.canvas,
            text="Sair",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_white"],
            bg="#ef4444",
            activebackground="#dc2626",
            activeforeground="white",
            bd=0,
            padx=16,
            pady=5,
            cursor="hand2",
            command=self._on_logout
        )
        self.btn_logout_window = self.canvas.create_window(1200, 24, window=self.btn_logout, anchor="ne")

        # 5. NavCards Flutuantes Individuais (SEM container escuro por trás)
        self.card_truck = NavCard(
            self.canvas,
            title="Alinhamento",
            icon_name="truck",
            command=lambda: self.router.navigate("trucks"),
            width=220,
            height=120
        )
        self.card_truck_window = self.canvas.create_window(388, 600, window=self.card_truck, anchor="s")

        self.card_history = NavCard(
            self.canvas,
            title="Histórico",
            icon_name="file_text",
            command=lambda: self.router.navigate("attendances"),
            width=220,
            height=120
        )
        self.card_history_window = self.canvas.create_window(640, 600, window=self.card_history, anchor="s")

        self.card_clients = NavCard(
            self.canvas,
            title="Clientes",
            icon_name="users",
            command=lambda: self.router.navigate("clientes.index"),
            width=220,
            height=120
        )
        self.card_clients_window = self.canvas.create_window(892, 600, window=self.card_clients, anchor="s")

        # Evento de Redimensionamento para ajustar layout e imagem de fundo
        self.canvas.bind("<Configure>", self._on_resize)

        # Iniciar Relógio Digital
        self._update_clock()

    def _update_clock(self):
        """Atualiza o relógio digital gigante (HH:mm) transparente no Canvas."""
        current_time = time.strftime("%H:%M")
        self.canvas.itemconfig(self.clock_text_id, text=current_time)
        self.clock_after_id = self.after(1000, self._update_clock)

    def _show_settings_menu(self):
        """Exibe o menu popup de configurações sob o botão de engrenagem."""
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_card"], fg=COLORS["text_white"], activebackground=COLORS["accent_blue"])
        
        menu.add_command(
            label="🏷️  Gerenciar Marcas de Veículos",
            command=lambda: self.router.navigate("configuracoes.marcas")
        )
        menu.add_command(
            label="🚛  Gerenciar Modelos de Veículos",
            command=lambda: self.router.navigate("configuracoes.modelos")
        )
        menu.add_separator()
        menu.add_command(
            label="🖼️  Alterar Imagem de Fundo",
            command=self._change_background_image
        )
        menu.add_command(
            label="🗑️  Remover Imagem de Fundo",
            command=self._remove_background_image,
            foreground=COLORS["danger"]
        )

        x = self.btn_settings.winfo_rootx()
        y = self.btn_settings.winfo_rooty() + self.btn_settings.winfo_height() + 4
        menu.tk_popup(x, y)

    def _change_background_image(self):
        """Abre o seletor de arquivos para enviar uma foto personalizada para o fundo."""
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem de Fundo",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if file_path:
            state.custom_bg_path = file_path
            save_user_settings({"custom_bg_path": file_path})
            self._apply_background()

    def _remove_background_image(self):
        """Restaura o fundo escuro padrão (#111520)."""
        state.custom_bg_path = None
        save_user_settings({"custom_bg_path": None})
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
            self.bg_image_id = None
        self._apply_background()

    def _on_logout(self):
        """Confirmação e logout imediato."""
        if messagebox.askyesno("Encerrar Sessão", "Deseja realmente encerrar a sessão do sistema?"):
            self.quit()

    def _apply_background(self):
        """Desenha a imagem de fundo personalizada de forma otimizada sem artefatos."""
        w = self.winfo_width() or self.canvas.winfo_width() or 1280
        h = self.winfo_height() or self.canvas.winfo_height() or 720

        if state.custom_bg_path:
            try:
                img = Image.open(state.custom_bg_path)
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                self.bg_photo = pil_to_photoimage(img)
                
                if self.bg_image_id:
                    self.canvas.itemconfig(self.bg_image_id, image=self.bg_photo)
                else:
                    self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                    self.canvas.tag_lower(self.bg_image_id)
            except Exception as e:
                print("Erro ao carregar imagem de fundo:", e)
                state.custom_bg_path = None
        else:
            if self.bg_image_id:
                self.canvas.delete(self.bg_image_id)
                self.bg_image_id = None
            self.canvas.configure(bg=COLORS["bg_dark"])

    def _on_resize(self, event):
        """Atualiza dinamicamente o posicionamento de cada elemento flutuante ao redimensionar."""
        w, h = event.width, event.height

        # Posições do Relógio e Botões no topo direito
        self.canvas.coords(self.btn_logout_window, w - 36, 24)
        self.canvas.coords(self.btn_settings_window, w - 120, 24)
        self.canvas.coords(self.clock_text_id, w - 36, 95)

        # Posições dos 3 Cards flutuantes na base
        self.canvas.coords(self.card_truck_window, w / 2 - 252, h - 48)
        self.canvas.coords(self.card_history_window, w / 2, h - 48)
        self.canvas.coords(self.card_clients_window, w / 2 + 252, h - 48)

        self._apply_background()

    def destroy(self):
        """Cancela timers ativos ao desmontar a view."""
        if self.clock_after_id:
            self.after_cancel(self.clock_after_id)
        super().destroy()
