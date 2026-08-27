"""
Ponto de entrada principal da aplicação desktop Tkinter.
Responsabilidades:
1. Inicializar e autenticar o banco de dados criptografado SQLCipher.
2. Executar migrações e seeders de dados iniciais.
3. Inicializar a janela Tkinter principal em tela cheia / maximizado.
4. Configurar o layout raiz e o roteador de telas.
5. Registrar rotas e carregar a tela inicial (Dashboard).
6. Encerrar conexões com o banco ao fechar.
"""
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Garantir que o diretório raiz está no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config.settings import COLORS
from app.database.connection import close_connection, DatabaseError
from app.database.migrations import run_migrations
from app.views.layouts.main_layout import MainLayout
from app.views.dashboard.index import DashboardView
from app.views.clientes.index import ClientesIndexView
from app.views.clientes.create import ClientCreateView
from app.views.clientes.edit import ClientEditView
from app.views.clientes.show import ClientShowView
from app.views.trucks.index import TrucksIndexView
from app.views.trucks.setup import TrucksSetupView
from app.views.trucks.medidas import TrucksMedidasView
from app.views.trucks.finalizar import TrucksFinalizarView
from app.views.trucks.preview import TrucksPreviewView
from app.views.attendances.index import AttendancesIndexView
from app.views.configuracoes.marcas import MarcasView
from app.views.configuracoes.modelos import ModelosView

def main():
    # Inicialização da camada de persistência e segurança (SQLCipher)
    try:
        run_migrations()
    except DatabaseError as err:
        root_tmp = tk.Tk()
        root_tmp.withdraw()
        messagebox.showerror(
            "Erro de Segurança do Banco de Dados",
            f"Não foi possível acessar a base de dados criptografada:\n\n{err}"
        )
        root_tmp.destroy()
        sys.exit(1)
    except Exception as err:
        root_tmp = tk.Tk()
        root_tmp.withdraw()
        messagebox.showerror(
            "Erro ao Inicializar Banco de Dados",
            "Ocorreu um erro ao conectar ao banco de dados. O sistema será encerrado."
        )
        root_tmp.destroy()
        sys.exit(1)

    root = tk.Tk()
    root.title("Sistema de Alinhamento - Oficina Desktop")
    root.configure(bg=COLORS["bg_dark"])

    # Tratamento de encerramento correto do programa
    def on_closing():
        close_connection()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Sempre abrir em tela cheia / maximizado
    try:
        root.attributes("-zoomed", True)
    except Exception:
        try:
            root.state("zoomed")
        except Exception:
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{sw}x{sh}+0+0")

    root.minsize(1024, 600)

    # Inicializar Layout Raiz
    layout = MainLayout(root)
    router = layout.router

    # Registrar Rotas da Aplicação
    router.register("dashboard", lambda parent, r, kwargs: DashboardView(parent, r, kwargs))
    router.register("trucks", lambda parent, r, kwargs: TrucksIndexView(parent, r, kwargs))
    router.register("trucks.setup", lambda parent, r, kwargs: TrucksSetupView(parent, r, kwargs))
    router.register("trucks.medidas", lambda parent, r, kwargs: TrucksMedidasView(parent, r, kwargs))
    router.register("trucks.finalizar", lambda parent, r, kwargs: TrucksFinalizarView(parent, r, kwargs))
    router.register("trucks.preview", lambda parent, r, kwargs: TrucksPreviewView(parent, r, kwargs))
    router.register("attendances", lambda parent, r, kwargs: AttendancesIndexView(parent, r, kwargs))

    # Rotas do Módulo de Configurações (Marcas e Modelos)
    router.register("configuracoes.marcas", lambda parent, r, kwargs: MarcasView(parent, r, kwargs))
    router.register("configuracoes.modelos", lambda parent, r, kwargs: ModelosView(parent, r, kwargs))
    router.register("settings.marcas", lambda parent, r, kwargs: MarcasView(parent, r, kwargs))
    router.register("settings.modelos", lambda parent, r, kwargs: ModelosView(parent, r, kwargs))

    # Rotas do Módulo de Clientes
    router.register("clientes.index", lambda parent, r, kwargs: ClientesIndexView(parent, r, kwargs))
    router.register("clientes.create", lambda parent, r, kwargs: ClientCreateView(parent, r, kwargs))
    router.register("clientes.edit", lambda parent, r, kwargs: ClientEditView(parent, r, kwargs))
    router.register("clientes.show", lambda parent, r, kwargs: ClientShowView(parent, r, kwargs))

    # Sinônimos de Rotas (ex: /clients, /alinhamento.trucks.preview, etc.)
    router.register("clients", lambda parent, r, kwargs: ClientesIndexView(parent, r, kwargs))
    router.register("clients.create", lambda parent, r, kwargs: ClientCreateView(parent, r, kwargs))
    router.register("clients.edit", lambda parent, r, kwargs: ClientEditView(parent, r, kwargs))
    router.register("clients.show", lambda parent, r, kwargs: ClientShowView(parent, r, kwargs))
    router.register("alinhamento/trucks", lambda parent, r, kwargs: TrucksIndexView(parent, r, kwargs))
    router.register("alinhamento.trucks.setup", lambda parent, r, kwargs: TrucksSetupView(parent, r, kwargs))
    router.register("alinhamento.trucks.medidas", lambda parent, r, kwargs: TrucksMedidasView(parent, r, kwargs))
    router.register("alinhamento.trucks.finalizar", lambda parent, r, kwargs: TrucksFinalizarView(parent, r, kwargs))
    router.register("alinhamento.trucks.preview", lambda parent, r, kwargs: TrucksPreviewView(parent, r, kwargs))

    # Abrir a primeira tela (Dashboard)
    router.navigate("dashboard")

    # Verificação assíncrona de atualizações automáticas em segundo plano
    try:
        from app.services.update_service import UpdateService
        UpdateService.check_for_updates_async(root)
    except Exception:
        pass

    # Iniciar Loop Principal
    root.mainloop()

if __name__ == "__main__":
    main()
