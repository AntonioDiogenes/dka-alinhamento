"""
Gerenciador central de navegação de rotas e substituição de views Tkinter.
"""
import tkinter as tk
from typing import Dict, Type, Callable

class Router:
    """
    Controla o fluxo de navegação entre telas (Frames) na janela principal.
    Evita a criação de múltiplas janelas do sistema operacional.
    """
    def __init__(self, container: tk.Frame):
        self.container = container
        self.routes: Dict[str, Callable[[tk.Frame, 'Router', dict], tk.Frame]] = {}
        self.current_view: tk.Frame = None
        self.current_route: str = None

    def register(self, route_name: str, view_factory: Callable):
        """Registra uma fábrica/construtor de View para um nome de rota."""
        self.routes[route_name] = view_factory

    def navigate(self, route_name: str, **kwargs):
        """
        Navega para a rota especificada, desmontando a tela atual e exibindo a nova.
        """
        if route_name not in self.routes:
            raise KeyError(f"Rota '{route_name}' não encontrada no Router.")

        # Desmontar/Destruir a view atual se existir
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

        self.current_route = route_name
        factory = self.routes[route_name]

        # Instanciar a nova view passando container, router e parâmetros adicionais
        self.current_view = factory(self.container, self, kwargs)
        self.current_view.pack(fill="both", expand=True)
