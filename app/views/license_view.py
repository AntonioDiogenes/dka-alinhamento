"""
Tela Modal de Ativação / Erro de Licença (views/license_view.py).
Exibida quando:
  - Nenhuma chave serial está salva localmente, ou
  - A chave salva foi rejeitada pelo servidor (expirada, revogada, inativa, etc.)
"""
import threading
import tkinter as tk
from tkinter import ttk

from app.config.settings import COLORS, FONTS
from app.config.user_settings import set_serial_key
from app.services.license_service import validate_license, LicenseNetworkError


class LicenseView:
    """
    Janela Toplevel modal de ativação de licença.

    Parâmetros
    ----------
    root : tk.Tk
        Janela raiz da aplicação (pode estar escondida com .withdraw()).
    on_success : callable
        Chamado sem argumentos quando a licença é validada com sucesso.
    error_message : str, opcional
        Mensagem de erro pré-existente (ex: chave expirada) exibida ao abrir.
    """

    def __init__(self, root: tk.Tk, on_success, error_message: str = ""):
        self.root = root
        self.on_success = on_success
        self._build_window(error_message)

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------

    def _build_window(self, initial_error: str):
        self.win = tk.Toplevel(self.root)
        self.win.title("Ativação de Licença — DKA Alinhamento")
        self.win.configure(bg=COLORS["bg_dark"])
        self.win.overrideredirect(False)
        self.win.attributes("-topmost", True)
        self.win.resizable(False, False)
        # Impedir fechar sem licença válida
        self.win.protocol("WM_DELETE_WINDOW", self._on_close_blocked)

        w, h = 480, 360
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.win.geometry(f"{w}x{h}+{x}+{y}")

        # --- Card principal ---
        card = tk.Frame(
            self.win,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["accent_blue"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # Ícone + título
        tk.Label(
            card,
            text="🔑  Ativação de Licença",
            font=("Segoe UI", 17, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
        ).pack(anchor="w", padx=24, pady=(24, 2))

        tk.Label(
            card,
            text="Insira a chave serial fornecida para liberar o acesso ao sistema.",
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            wraplength=420,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 20))

        # Campo de entrada
        tk.Label(
            card,
            text="Chave Serial",
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w", padx=24)

        entry_frame = tk.Frame(
            card,
            bg=COLORS["border_subtle"],
            highlightbackground=COLORS["border_subtle"],
            highlightthickness=1,
        )
        entry_frame.pack(fill="x", padx=24, pady=(4, 0))

        self.entry_key = tk.Entry(
            entry_frame,
            font=("Segoe UI", 12),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["text_white"],
            relief="flat",
            bd=0,
        )
        self.entry_key.pack(fill="x", padx=8, pady=8)
        self.entry_key.bind("<Return>", lambda _e: self._on_activate())
        self.entry_key.focus_set()

        # Mensagem de erro / status
        self.lbl_error = tk.Label(
            card,
            text=initial_error,
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["danger"],
            wraplength=420,
            justify="left",
        )
        self.lbl_error.pack(anchor="w", padx=24, pady=(8, 0))

        # Separador
        tk.Frame(card, bg=COLORS["border_subtle"], height=1).pack(
            fill="x", padx=24, pady=(20, 0)
        )

        # Botão Ativar
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", padx=24, pady=16)

        self.btn_activate = tk.Button(
            btn_frame,
            text="Ativar Sistema",
            font=FONTS["button"],
            bg=COLORS["accent_blue"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_blue_hover"],
            activeforeground=COLORS["text_white"],
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._on_activate,
        )
        self.btn_activate.pack(side="right")

        # Barra de progresso (oculta inicialmente)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "License.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_dark"],
            background=COLORS["accent_blue"],
            thickness=4,
        )
        self.progress = ttk.Progressbar(
            card,
            style="License.Horizontal.TProgressbar",
            orient="horizontal",
            mode="indeterminate",
        )
        # Não empacotado ainda — aparece só durante validação

    # ------------------------------------------------------------------
    # Lógica de ativação
    # ------------------------------------------------------------------

    def _set_loading(self, is_loading: bool):
        """Alterna entre estado de carregamento e estado normal."""
        if is_loading:
            self.btn_activate.config(state="disabled", text="Validando...")
            self.entry_key.config(state="disabled")
            self.progress.pack(fill="x", padx=24, pady=(0, 4))
            self.progress.start(10)
            self._set_error("")
        else:
            self.progress.stop()
            self.progress.pack_forget()
            self.btn_activate.config(state="normal", text="Ativar Sistema")
            self.entry_key.config(state="normal")

    def _set_error(self, message: str):
        self.lbl_error.config(text=message, fg=COLORS["danger"])

    def _set_success_msg(self, message: str):
        self.lbl_error.config(text=f"✓ {message}", fg="#10b981")

    def _on_activate(self):
        key = self.entry_key.get().strip()
        if not key:
            self._set_error("Por favor, insira a chave serial.")
            return

        self._set_loading(True)
        thread = threading.Thread(
            target=self._validate_thread, args=(key,), daemon=True
        )
        thread.start()

    def _validate_thread(self, key: str):
        """Executa em thread separada para não travar a UI."""
        try:
            result = validate_license(key)
        except LicenseNetworkError as exc:
            err_msg = str(exc)
            self.root.after(0, lambda: self._handle_result(None, err_msg))
            return

        self.root.after(0, lambda: self._handle_result(result, None))

    def _handle_result(self, result: dict | None, network_error: str | None):
        self._set_loading(False)

        if network_error:
            self._set_error(f"Erro de conexão: {network_error}")
            return

        if result and result.get("valid") is True:
            key = self.entry_key.get().strip()
            set_serial_key(key)
            client_name = ""
            try:
                client_name = result["data"]["client"]["name"]
            except (KeyError, TypeError):
                pass
            msg = result.get("message", "Licença ativada com sucesso!")
            if client_name:
                msg = f"{msg} ({client_name})"
            self._set_success_msg(msg)
            # Pequeno delay para o usuário ver a mensagem de sucesso
            self.root.after(800, self._finalize_success)
        else:
            error_msg = result.get("message", "Chave inválida ou não autorizada.") if result else "Resposta inesperada do servidor."
            self._set_error(error_msg)

    def _finalize_success(self):
        self.win.destroy()
        if self.on_success:
            self.on_success()

    def _on_close_blocked(self):
        """Impede fechar a janela sem ter uma licença válida."""
        import sys
        sys.exit(0)
