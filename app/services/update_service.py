"""
Serviço de Atualização Automática, Splash Screen e Ícone da Bandeja / Segundo Plano (services/update_service.py).
Responsabilidades:
1. Exibir Tela de Splash (Carregamento / Buscando Atualizações) ao iniciar o app.
2. Verificar atualizações em segundo plano e exibir progresso caso haja versão nova.
3. Gerenciar o minimização do app para o Segundo Plano (Bandeja / System Tray do Windows) ao fechar (X).
"""
import os
import sys
import json
import time
import ssl
import threading
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from app.config.version import CURRENT_VERSION, APP_NAME, VERSION_CHECK_URL
from app.config.settings import COLORS, FONTS

def _urlopen_with_ssl(req, timeout=None):
    """Executa urlopen com validação SSL e faz fallback para unverified caso falhe no Windows/PyInstaller."""
    try:
        if timeout:
            return urllib.request.urlopen(req, timeout=timeout)
        return urllib.request.urlopen(req)
    except Exception as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "certificate verify failed" in str(e):
            ctx = ssl._create_unverified_context()
            if timeout:
                return urllib.request.urlopen(req, timeout=timeout, context=ctx)
            return urllib.request.urlopen(req, context=ctx)
        raise e


# Suporte opcional ao Pystray para ícone na bandeja perto do relógio do Windows
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


class UpdateService:
    def __init__(self, root, on_app_ready_callback=None):
        self.root = root
        self.on_app_ready_callback = on_app_ready_callback
        self.splash_window = None
        self.download_window = None
        self.progress_bar = None
        self.status_label = None

    @classmethod
    def show_splash_and_check(cls, root, on_app_ready_callback):
        """Exibe a tela de carregamento 'Buscando atualizações...' e verifica a versão."""
        service = cls(root, on_app_ready_callback)
        service._create_splash_window()
        
        # Dispara a checagem em thread separada
        thread = threading.Thread(target=service._check_for_updates_thread, daemon=True)
        thread.start()
        return service

    def _create_splash_window(self):
        """Cria uma tela de Splash elegante e moderna de carregamento."""
        self.splash_window = tk.Toplevel(self.root)
        self.splash_window.title("Iniciando DKA Alinhamento")
        self.splash_window.configure(bg=COLORS["bg_dark"])
        self.splash_window.overrideredirect(True) # Remove bordas de janela do SO
        self.splash_window.attributes("-topmost", True)

        # Centralizar na tela
        w, h = 420, 240
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.splash_window.geometry(f"{w}x{h}+{x}+{y}")

        # Container Principal
        container = tk.Frame(
            self.splash_window,
            bg=COLORS["bg_card"],
            bd=1,
            relief="solid",
            highlightbackground=COLORS["accent_blue"],
            highlightthickness=1
        )
        container.pack(fill="both", expand=True)

        # Título / Logo
        lbl_logo = tk.Label(
            container,
            text="DKA ALINHAMENTO",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["accent_blue"]
        )
        lbl_logo.pack(anchor="center", pady=(35, 5))

        lbl_version = tk.Label(
            container,
            text=f"Versão {CURRENT_VERSION} • Oficina Desktop",
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        lbl_version.pack(anchor="center", pady=(0, 25))

        # Estilo para Barra de Carregamento
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_dark"],
            background=COLORS["accent_blue"],
            thickness=8
        )

        self.splash_progress = ttk.Progressbar(
            container,
            style="Splash.Horizontal.TProgressbar",
            orient="horizontal",
            mode="indeterminate"
        )
        self.splash_progress.pack(fill="x", padx=40, pady=(0, 15))
        self.splash_progress.start(10)

        # Texto de Status
        self.splash_status = tk.Label(
            container,
            text="🔍 Buscando atualizações do sistema...",
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"]
        )
        self.splash_status.pack(anchor="center")

    def _check_for_updates_thread(self):
        """Thread que faz a busca por atualizações no servidor."""
        start_time = time.time()
        latest_version = None
        download_url = ""
        release_notes = ""
        has_update = False

        try:
            req = urllib.request.Request(
                VERSION_CHECK_URL,
                headers={"User-Agent": f"{APP_NAME}-AutoUpdater"}
            )
            with _urlopen_with_ssl(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    latest_version = data.get("version", "").strip()
                    
                    if latest_version and self._is_newer_version(CURRENT_VERSION, latest_version):
                        has_update = True
                        download_url = self._get_platform_download_url(data)
                        release_notes = data.get("release_notes", "Melhorias gerais e correções.")
        except Exception:
            pass

        # Garante um tempo mínimo de exibição do splash (1.2 segundos) para ficar esteticamente agradável
        elapsed = time.time() - start_time
        if elapsed < 1.2:
            time.sleep(1.2 - elapsed)

        if has_update and latest_version:
            # Atualização encontrada -> Fecha o splash e abre o diálogo de atualização
            self.root.after(0, self._transition_to_update_dialog, latest_version, download_url, release_notes)
        else:
            # Sistema já atualizado -> Atualiza o splash e abre a aplicação principal
            self.root.after(0, self._transition_to_main_app)

    def _transition_to_main_app(self):
        """Atualiza a mensagem de sucesso e exibe a aplicação principal."""
        if self.splash_status:
            self.splash_status.config(text="✓ Sistema atualizado! Carregando...", fg="#10b981")
        if self.splash_progress:
            self.splash_progress.stop()

        self.root.after(500, self._close_splash_and_open_main)

    def _close_splash_and_open_main(self):
        if self.splash_window:
            self.splash_window.destroy()
            self.splash_window = None
        
        if self.on_app_ready_callback:
            self.on_app_ready_callback()

    def _transition_to_update_dialog(self, latest_version, download_url, release_notes):
        if self.splash_window:
            self.splash_window.destroy()
            self.splash_window = None
        
        self._show_update_available_dialog(latest_version, download_url, release_notes)

    def _is_newer_version(self, current: str, latest: str) -> bool:
        try:
            c_parts = [int(x) for x in current.lstrip('v').split('.')]
            l_parts = [int(x) for x in latest.lstrip('v').split('.')]
            return l_parts > c_parts
        except Exception:
            return False

    def _get_platform_download_url(self, data: dict) -> str:
        if sys.platform.startswith("win"):
            return data.get("download_url_win", "")
        elif sys.platform == "darwin":
            return data.get("download_url_mac", "")
        else:
            return data.get("download_url_linux", "")

    def _show_update_available_dialog(self, latest_version: str, download_url: str, release_notes: str):
        dialog = tk.Toplevel(self.root)
        dialog.title("🚀 Atualização Disponível")
        dialog.configure(bg=COLORS["bg_dark"])
        if self.root.state() != "withdrawn":
            dialog.transient(self.root)
        dialog.attributes("-topmost", True)
        dialog.lift()
        dialog.focus_force()
        dialog.grab_set()

        w, h = 500, 360
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.resizable(False, False)

        container = tk.Frame(dialog, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border_subtle"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        lbl_header = tk.Label(
            container,
            text=f"🚀 Nova Versão Disponível ({latest_version})",
            font=FONTS["header_title"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"]
        )
        lbl_header.pack(anchor="w", padx=20, pady=(20, 5))

        lbl_version_info = tk.Label(
            container,
            text=f"Sua versão atual é a v{CURRENT_VERSION}. Recomendamos atualizar agora para obter as últimas novidades.",
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            wraplength=440,
            justify="left"
        )
        lbl_version_info.pack(anchor="w", padx=20, pady=(0, 15))

        lbl_notes_title = tk.Label(container, text="Novidades desta versão:", font=FONTS["card_title"], bg=COLORS["bg_card"], fg=COLORS["accent_blue"])
        lbl_notes_title.pack(anchor="w", padx=20, pady=(0, 5))

        txt_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        txt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        txt_notes = tk.Text(txt_frame, font=FONTS["body"], bg=COLORS["bg_dark"], fg=COLORS["text_white"], bd=0, wrap="word", height=5)
        txt_notes.insert("1.0", release_notes)
        txt_notes.configure(state="disabled")
        txt_notes.pack(fill="both", expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(container, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        def on_later():
            dialog.destroy()
            if self.on_app_ready_callback:
                self.on_app_ready_callback()

        def on_update():
            dialog.destroy()
            self._start_download_and_install(latest_version, download_url)

        btn_later = tk.Button(
            btn_frame,
            text="Lembrar Mais Tarde",
            font=FONTS["button"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_muted"],
            activebackground=COLORS["bg_dark"],
            activeforeground=COLORS["text_white"],
            bd=1,
            relief="solid",
            command=on_later,
            cursor="hand2",
            padx=15,
            pady=6
        )
        btn_later.pack(side="left")

        btn_update = tk.Button(
            btn_frame,
            text="🚀 Baixar e Atualizar Agora",
            font=FONTS["button"],
            bg=COLORS["accent_blue"],
            fg=COLORS["text_white"],
            activebackground=COLORS["accent_blue_hover"],
            activeforeground=COLORS["text_white"],
            bd=0,
            command=on_update,
            cursor="hand2",
            padx=15,
            pady=6
        )
        btn_update.pack(side="right")

    def _start_download_and_install(self, latest_version: str, download_url: str):
        self.download_window = tk.Toplevel(self.root)
        self.download_window.title("Baixando Atualização...")
        self.download_window.configure(bg=COLORS["bg_dark"])
        if self.root.state() != "withdrawn":
            self.download_window.transient(self.root)
        self.download_window.attributes("-topmost", True)
        self.download_window.lift()
        self.download_window.focus_force()
        self.download_window.grab_set()

        w, h = 480, 200
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.download_window.geometry(f"{w}x{h}+{x}+{y}")
        self.download_window.resizable(False, False)

        container = tk.Frame(self.download_window, bg=COLORS["bg_card"], bd=1, relief="solid")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        lbl_title = tk.Label(
            container,
            text=f"Baixando {APP_NAME} (v{latest_version})...",
            font=FONTS["header_title"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"]
        )
        lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS["bg_dark"],
            background=COLORS["accent_blue"],
            thickness=16
        )

        self.progress_bar = ttk.Progressbar(
            container,
            style="Custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(fill="x", padx=20, pady=10)

        self.status_label = tk.Label(
            container,
            text="Iniciando download...",
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self.status_label.pack(anchor="w", padx=20, pady=(5, 15))

        thread = threading.Thread(
            target=self._download_worker,
            args=(download_url,),
            daemon=True
        )
        thread.start()

    def _download_worker(self, download_url: str):
        try:
            if not download_url:
                raise ValueError("URL de download inválida ou vazia.")

            if sys.platform.startswith("win"):
                target_filename = "DKA_Alinhamento_novo.exe"
            elif download_url.endswith(".tar.gz"):
                target_filename = "DKA_Alinhamento_novo.tar.gz"
            elif download_url.endswith(".zip"):
                target_filename = "DKA_Alinhamento_novo.zip"
            else:
                target_filename = "DKA_Alinhamento_novo"

            download_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent.parent
            destination_path = download_dir / target_filename

            req = urllib.request.Request(download_url, headers={"User-Agent": f"{APP_NAME}-AutoUpdater"})
            with _urlopen_with_ssl(req) as response:
                total_length = response.getheader('content-length')
                total_bytes = int(total_length) if total_length else 0
                
                downloaded_bytes = 0
                chunk_size = 64 * 1024

                with open(destination_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded_bytes += len(chunk)

                        if total_bytes > 0:
                            percent = (downloaded_bytes / total_bytes) * 100
                            mb_downloaded = downloaded_bytes / (1024 * 1024)
                            mb_total = total_bytes / (1024 * 1024)
                            msg = f"Baixando: {mb_downloaded:.1f} MB / {mb_total:.1f} MB ({percent:.0f}%)"
                        else:
                            mb_downloaded = downloaded_bytes / (1024 * 1024)
                            percent = 50
                            msg = f"Baixando: {mb_downloaded:.1f} MB..."

                        self.root.after(0, lambda p=percent, m=msg: self._update_progress_ui(p, m))

            self.root.after(0, lambda: self._update_progress_ui(100, "✓ Download concluído! Reiniciando a aplicação..."))
            time.sleep(1.2)
            self.root.after(0, lambda: self._apply_update_and_restart(destination_path))

        except Exception as err:
            err_msg = str(err)
            self.root.after(0, lambda: self._show_download_error(err_msg))

    def _update_progress_ui(self, percent: float, status_text: str):
        if self.progress_bar and self.status_label:
            self.progress_bar['value'] = percent
            self.status_label.config(text=status_text)

    def _show_download_error(self, error_message: str):
        if self.download_window:
            self.download_window.destroy()
        messagebox.showerror(
            "Erro no Download",
            f"Não foi possível baixar a atualização:\n\n{error_message}"
        )

    def _apply_update_and_restart(self, new_file_path: Path):
        current_exe = Path(sys.executable)
        exe_dir = current_exe.parent
        current_exe_name = current_exe.name
        new_file_name = new_file_path.name

        if sys.platform.startswith("win"):
            bat_script = exe_dir / "updater.bat"
            bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
if exist "{current_exe_name}" del /f /q "{current_exe_name}"
if exist "{new_file_name}" move /y "{new_file_name}" "{current_exe_name}"
start "" "{current_exe_name}"
del "%~f0"
"""
            with open(bat_script, "w") as f:
                f.write(bat_content)

            subprocess.Popen(
                ["cmd.exe", "/c", str(bat_script)],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                close_fds=True
            )
        else:
            sh_script = exe_dir / "updater.sh"
            sh_content = f"""#!/bin/bash
sleep 2
if [[ "{new_file_name}" == *.tar.gz ]]; then
    tar -xzf "{new_file_name}" -C "{exe_dir}"
    rm -f "{new_file_name}"
elif [[ "{new_file_name}" == *.zip ]]; then
    unzip -o "{new_file_name}" -d "{exe_dir}"
    rm -f "{new_file_name}"
else
    rm -f "{current_exe_name}"
    mv "{new_file_name}" "{current_exe_name}"
fi
chmod +x "{exe_dir}/{current_exe_name}"
"{exe_dir}/{current_exe_name}" &
rm -- "$0"
"""
            with open(sh_script, "w") as f:
                f.write(sh_content)
            os.chmod(sh_script, 0o755)

            subprocess.Popen(["/bin/bash", str(sh_script)], close_fds=True)

        sys.exit(0)


class SystemTrayManager:
    """Gerencia a minimização para o segundo plano (Bandeja do Sistema / System Tray)."""

    def __init__(self, root, on_quit_callback):
        self.root = root
        self.on_quit_callback = on_quit_callback
        self.tray_icon = None
        self.is_minimized_to_tray = False

    def setup(self):
        """Configura a interceptação do botão de fechar (X)."""
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def minimize_to_tray(self):
        """Esconde a janela principal e minimiza para o segundo plano."""
        self.root.withdraw()
        self.is_minimized_to_tray = True

        if HAS_PYSTRAY and not self.tray_icon:
            # Criar um ícone simples para a bandeja do sistema caso pystray esteja presente
            image = self._create_icon_image()
            menu = pystray.Menu(
                pystray.MenuItem("🖥️ Abrir DKA Alinhamento", self.restore_from_tray, default=True),
                pystray.MenuItem("❌ Sair do Aplicativo", self.quit_app)
            )
            self.tray_icon = pystray.Icon("DKAAlinhamento", image, "DKA Alinhamento", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        """Restaura a janela principal do segundo plano para o primeiro plano."""
        self.root.after(0, self._restore_ui)

    def _restore_ui(self):
        self.root.deiconify()
        try:
            self.root.state("zoomed")
        except Exception:
            pass
        self.root.focus_force()
        self.is_minimized_to_tray = False

    def quit_app(self, icon=None, item=None):
        """Encerra completamente a aplicação."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self._final_quit)

    def _final_quit(self):
        if self.on_quit_callback:
            self.on_quit_callback()
        self.root.destroy()
        sys.exit(0)

    def _create_icon_image(self):
        """Gera um ícone azul de 64x64 em memória para a bandeja."""
        width, height = 64, 64
        image = Image.new('RGB', (width, height), color='#111520')
        dc = ImageDraw.Draw(image)
        dc.rectangle([8, 8, 56, 56], fill='#4f77ff')
        return image
