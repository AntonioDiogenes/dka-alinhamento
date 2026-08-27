"""
Serviço de Atualização Automática e Download Transparente (services/update_service.py).
Responsabilidades:
1. Verificar atualizações em segundo plano (Thread assíncrona) sem travar a interface.
2. Exibir janela modal customizada com barra de progresso Tkinter durante o download.
3. Substituir o executável antigo pelo novo usando script fantasma (updater.bat / updater.sh).
4. Reiniciar a aplicação atualizada automaticamente.
"""
import os
import sys
import json
import time
import shutil
import threading
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from app.config.version import CURRENT_VERSION, APP_NAME, VERSION_CHECK_URL
from app.config.settings import COLORS, FONTS

class UpdateService:
    def __init__(self, root):
        self.root = root
        self.download_window = None
        self.progress_bar = None
        self.status_label = None
        self.percent_label = None

    @classmethod
    def check_for_updates_async(cls, root):
        """Método estático de conveniência para disparar a checagem ao abrir o app."""
        service = cls(root)
        thread = threading.Thread(target=service._check_for_updates_thread, daemon=True)
        thread.start()

    def _check_for_updates_thread(self):
        """Thread em segundo plano que faz o GET na URL da versão."""
        try:
            req = urllib.request.Request(
                VERSION_CHECK_URL,
                headers={"User-Agent": f"{APP_NAME}-AutoUpdater"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    latest_version = data.get("version", "").strip()
                    
                    if latest_version and self._is_newer_version(CURRENT_VERSION, latest_version):
                        # Seleciona a URL de download apropriada para o SO atual
                        download_url = self._get_platform_download_url(data)
                        release_notes = data.get("release_notes", "Correções de bugs e melhorias gerais.")
                        
                        # Executa a exibição da janela na thread principal do Tkinter
                        self.root.after(
                            0,
                            lambda: self._show_update_available_dialog(latest_version, download_url, release_notes)
                        )
        except Exception as err:
            # Se o cliente estiver offline ou o servidor fora, ignora silenciosamente
            pass

    def _is_newer_version(self, current: str, latest: str) -> bool:
        """Compara strings de versão numéricas (ex: '1.0.0' < '1.0.1')."""
        try:
            c_parts = [int(x) for x in current.lstrip('v').split('.')]
            l_parts = [int(x) for x in latest.lstrip('v').split('.')]
            return l_parts > c_parts
        except Exception:
            return False

    def _get_platform_download_url(self, data: dict) -> str:
        """Retorna a URL correspondente ao SO do cliente (Windows, Linux ou macOS)."""
        if sys.platform.startswith("win"):
            return data.get("download_url_win", "")
        elif sys.platform == "darwin":
            return data.get("download_url_mac", "")
        else:
            return data.get("download_url_linux", "")

    def _show_update_available_dialog(self, latest_version: str, download_url: str, release_notes: str):
        """Exibe a janela modal informando que existe uma nova versão disponível."""
        dialog = tk.Toplevel(self.root)
        dialog.title("🚀 Atualização Disponível")
        dialog.configure(bg=COLORS["bg_dark"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Centralizar na tela
        w, h = 500, 360
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.resizable(False, False)

        # Container Principal
        container = tk.Frame(dialog, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border_subtle"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Cabeçalho
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

        # Quadro de Notas da Versão (Release Notes)
        lbl_notes_title = tk.Label(container, text="Novidades desta versão:", font=FONTS["card_title"], bg=COLORS["bg_card"], fg=COLORS["accent_blue"])
        lbl_notes_title.pack(anchor="w", padx=20, pady=(0, 5))

        txt_frame = tk.Frame(container, bg=COLORS["bg_dark"])
        txt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        txt_notes = tk.Text(txt_frame, font=FONTS["body"], bg=COLORS["bg_dark"], fg=COLORS["text_white"], bd=0, wrap="word", height=5)
        txt_notes.insert("1.0", release_notes)
        txt_notes.configure(state="disabled")
        txt_notes.pack(fill="both", expand=True, padx=8, pady=8)

        # Botões de Ação
        btn_frame = tk.Frame(container, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        def on_later():
            dialog.destroy()

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
        """Abre a janela com a barra de progresso e inicia o download."""
        self.download_window = tk.Toplevel(self.root)
        self.download_window.title("Baixando Atualização...")
        self.download_window.configure(bg=COLORS["bg_dark"])
        self.download_window.transient(self.root)
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

        # Estilo para ttk.Progressbar
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

        # Status text (ex: 4.2 MB / 15.0 MB - 28%)
        self.status_label = tk.Label(
            container,
            text="Iniciando download...",
            font=FONTS["sublabel"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"]
        )
        self.status_label.pack(anchor="w", padx=20, pady=(5, 15))

        # Disparar download em thread para manter a barra de progresso suave
        thread = threading.Thread(
            target=self._download_worker,
            args=(download_url,),
            daemon=True
        )
        thread.start()

    def _download_worker(self, download_url: str):
        """Baixa o arquivo em blocos (chunks) e atualiza a barra de progresso."""
        try:
            if not download_url:
                raise ValueError("URL de download inválida ou vazia.")

            # Define o local do arquivo temporário baixado
            target_filename = "DKA_Alinhamento_novo.exe" if sys.platform.startswith("win") else "DKA_Alinhamento_novo"
            download_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent.parent
            destination_path = download_dir / target_filename

            req = urllib.request.Request(download_url, headers={"User-Agent": f"{APP_NAME}-AutoUpdater"})
            with urllib.request.urlopen(req) as response:
                total_length = response.getheader('content-length')
                total_bytes = int(total_length) if total_length else 0
                
                downloaded_bytes = 0
                chunk_size = 64 * 1024  # 64 KB per chunk

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

            # Download Concluído!
            self.root.after(0, lambda: self._update_progress_ui(100, "✓ Download concluído! Reiniciando a aplicação..."))
            time.sleep(1.2)
            
            # Dispara a auto-substituição e reinicialização
            self.root.after(0, lambda: self._apply_update_and_restart(destination_path))

        except Exception as err:
            err_msg = str(err)
            self.root.after(0, lambda: self._show_download_error(err_msg))

    def _update_progress_ui(self, percent: float, status_text: str):
        """Atualiza o widget Tkinter na thread principal."""
        if self.progress_bar and self.status_label:
            self.progress_bar['value'] = percent
            self.status_label.config(text=status_text)

    def _show_download_error(self, error_message: str):
        if self.download_window:
            self.download_window.destroy()
        messagebox.showerror(
            "Erro no Download",
            f"Não foi possível baixar a atualização:\n\n{error_message}\n\nPor favor, tente novamente mais tarde."
        )

    def _apply_update_and_restart(self, new_file_path: Path):
        """Cria o script fantasma de substituição e fecha o app antigo."""
        current_exe = Path(sys.executable)
        exe_dir = current_exe.parent
        current_exe_name = current_exe.name
        new_file_name = new_file_path.name

        if sys.platform.startswith("win"):
            # Script .bat para Windows
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

            # Executa cmd.exe em segundo plano
            subprocess.Popen(
                ["cmd.exe", "/c", str(bat_script)],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                close_fds=True
            )
        else:
            # Script .sh para Linux/macOS
            sh_script = exe_dir / "updater.sh"
            sh_content = f"""#!/bin/bash
sleep 2
rm -f "{current_exe_name}"
mv "{new_file_name}" "{current_exe_name}"
chmod +x "{current_exe_name}"
"./{current_exe_name}" &
rm -- "$0"
"""
            with open(sh_script, "w") as f:
                f.write(sh_content)
            os.chmod(sh_script, 0o755)

            subprocess.Popen(
                ["/bin/bash", str(sh_script)],
                close_fds=True
            )

        # Encerra o processo atual do Python/Tkinter para liberar o arquivo
        sys.exit(0)
