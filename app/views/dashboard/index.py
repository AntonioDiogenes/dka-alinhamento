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

        # 2. Container de Interface (Posicionado sobre o Canvas)
        self.main_container = tk.Frame(self.canvas, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.container_window = self.canvas.create_window(0, 0, window=self.main_container, anchor="nw")

        # Configurar grid responsivo do container principal
        self.main_container.grid_rowconfigure(0, weight=0) # Header
        self.main_container.grid_rowconfigure(1, weight=1) # Espaçador Flexível Central
        self.main_container.grid_rowconfigure(2, weight=0) # Base (Cards)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Evento de Redimensionamento para ajustar layout e imagem de fundo
        self.canvas.bind("<Configure>", self._on_resize)

        # Construção da Interface
        self._build_ui()

        # Iniciar Relógio Digital
        self._update_clock()

    def _build_ui(self):
        """Monta o layout limpo sem duplicações visuais."""
        # ==========================================
        # 1. SEÇÃO TOPO: HEADER DESKTOP
        # ==========================================
        self.header_frame = tk.Frame(self.main_container, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=36, pady=(32, 0))
        self.header_frame.grid_columnconfigure(0, weight=1) # Espaço à esquerda
        self.header_frame.grid_columnconfigure(1, weight=0) # Direita (Ações + Relógio)

        # CANTO SUPERIOR DIREITO — AÇÕES E RELÓGIO DIGITAL
        self.right_header = tk.Frame(self.header_frame, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.right_header.grid(row=0, column=1, sticky="ne")

        # Linha Superior (Botões de Ação: Engrenagem e Logout)
        self.actions_row = tk.Frame(self.right_header, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.actions_row.pack(anchor="e", pady=(0, 8))

        # Ícone Settings (Size 32)
        self.img_gear = create_icon_image("gear", size=32, color=COLORS["text_white"])
        self.btn_settings = tk.Button(
            self.actions_row,
            image=self.img_gear,
            bg=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._show_settings_menu
        )
        self.btn_settings.pack(side="left", padx=(0, 16))

        # Ícone LogOut (Size 32)
        self.img_logout = create_icon_image("logout", size=32, color=COLORS["text_white"])
        self.btn_logout = tk.Button(
            self.actions_row,
            image=self.img_logout,
            bg=COLORS["bg_dark"],
            activebackground=COLORS["bg_card"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._on_logout
        )
        self.btn_logout.pack(side="left")

        # Linha Inferior (Relógio Digital de Parede 64px)
        self.lbl_clock = tk.Label(
            self.right_header,
            text="00:00",
            font=FONTS["title_clock"],
            fg=COLORS["text_white"],
            bg=COLORS["bg_dark"]
        )
        self.lbl_clock.pack(anchor="e")

        # ==========================================
        # 2. ESPAÇADOR FLEXÍVEL CENTRAL (Ajuste Responsivo)
        # ==========================================
        self.spacer = tk.Frame(self.main_container, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.spacer.grid(row=1, column=0, sticky="nsew")

        # ==========================================
        # 3. SEÇÃO BASE: GRADE CENTRAL DE CARDS OPERACIONAIS
        # ==========================================
        self.cards_frame = tk.Frame(self.main_container, bg=COLORS["bg_dark"], bd=0, highlightthickness=0)
        self.cards_frame.grid(row=2, column=0, sticky="s", pady=(0, 64))

        # Criar os 3 NavCards centralizados horizontalmente
        # 1. Alinhamento Truck
        self.card_truck = NavCard(
            self.cards_frame,
            title="Alinhamento Truck",
            icon_name="truck",
            command=lambda: self.router.navigate("trucks"),
            width=220,
            height=120
        )
        self.card_truck.pack(side="left", padx=16)

        # 2. Histórico
        self.card_history = NavCard(
            self.cards_frame,
            title="Histórico",
            icon_name="file_text",
            command=lambda: self.router.navigate("attendances"),
            width=220,
            height=120
        )
        self.card_history.pack(side="left", padx=16)

        # 3. Clientes
        self.card_clients = NavCard(
            self.cards_frame,
            title="Clientes",
            icon_name="users",
            command=lambda: self.router.navigate("clientes.index"),
            width=220,
            height=120
        )
        self.card_clients.pack(side="left", padx=16)

    def _update_clock(self):
        """Atualiza o relógio digital gigante (HH:mm) a cada segundo."""
        current_time = time.strftime("%H:%M")
        self.lbl_clock.config(text=current_time)
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
            self._apply_background()

    def _remove_background_image(self):
        """Restaura o fundo escuro padrão (#111520)."""
        state.custom_bg_path = None
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
        """Atualiza dinamicamente as dimensões do container e da imagem de fundo ao redimensionar."""
        w, h = event.width, event.height
        self.canvas.itemconfig(self.container_window, width=w, height=h)
        self._apply_background()

    def destroy(self):
        """Cancela timers ativos ao desmontar a view."""
        if self.clock_after_id:
            self.after_cancel(self.clock_after_id)
        super().destroy()
