"""
Utilitário Multiplataforma para Rolagem com Roda do Mouse em Canvases Tkinter (utils/scroll_helper.py).
Suporta Linux (<Button-4>/<Button-5>), Windows e macOS (<MouseWheel>).
Vincular recursivamente aos widgets para garantir rolagem fluida ao passar o mouse por cima de elementos internos.
"""
import sys
import tkinter as tk

def setup_canvas_scrolling(canvas: tk.Canvas, inner_frame: tk.Widget = None):
    """
    Configura eventos de rolagem da roda do mouse em um Canvas e seus widgets filhos.
    """
    is_linux = sys.platform.startswith("linux")

    def _on_mousewheel(event):
        if is_linux:
            if event.num == 4:
                canvas.yview_scroll(-2, "units")
            elif event.num == 5:
                canvas.yview_scroll(2, "units")
        else:
            # Windows / macOS
            delta = int(-1 * (event.delta / 120))
            if delta == 0:
                delta = -1 if event.delta > 0 else 1
            canvas.yview_scroll(delta, "units")
        return "break"

    def _bind_widget(w):
        if is_linux:
            w.bind("<Button-4>", _on_mousewheel, add="+")
            w.bind("<Button-5>", _on_mousewheel, add="+")
        else:
            w.bind("<MouseWheel>", _on_mousewheel, add="+")

    _bind_widget(canvas)
    if inner_frame:
        _bind_widget(inner_frame)
        def _bind_recursive(parent):
            for child in parent.winfo_children():
                _bind_widget(child)
                _bind_recursive(child)
        
        _bind_recursive(inner_frame)
        inner_frame.bind("<Configure>", lambda e: _bind_recursive(inner_frame), add="+")

    return _on_mousewheel
