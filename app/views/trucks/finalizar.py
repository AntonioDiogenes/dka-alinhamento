"""
Tela 1 das Etapas Finais: Finalizar Alinhamento (views/trucks/finalizar.py).
Formulário em 3 Cards Principais:
Card 1: Veículos da Composição (Placa com máscara Mercosul/Antiga e KM por unidade).
Card 2: Proprietário / Cliente (Busca em tempo real, Card de Cliente Selecionado e Modal de Cadastro Rápido).
Card 3: Dados do Serviço (Técnico Responsável e Observações Técnicas).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional

from app.config.settings import COLORS
from app.services.client_service import ClientService
from app.components.alignment_header import AlignmentHeader
from app.utils.icons import create_icon_image
from app.utils.scroll_helper import setup_canvas_scrolling

ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

TECNICOS_LISTA = [
    "Carlos Eduardo - Mecânico Chefe",
    "João Pedro - Técnico Alinhador",
    "Roberto Silva - Especialista em Geometria",
    "Marcos Antonio - Técnico de Suspensão"
]

class QuickClientDialog(tk.Toplevel):
    """Modal Popup de Cadastro Rápido de Cliente sem sair do fluxo."""
    def __init__(self, parent: tk.Widget, on_save: Any):
        super().__init__(parent)
        self.title("Cadastro Rápido de Cliente")
        self.configure(bg="#272f43")
        self.geometry("520x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save

        self.var_nome = tk.StringVar()
        self.var_cpf = tk.StringVar()
        self.var_cel = tk.StringVar()
        self.var_cidade = tk.StringVar()
        self.var_uf = tk.StringVar(value="SP")

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg="#272f43", padx=24, pady=24)
        container.pack(fill="both", expand=True)

        lbl_t = tk.Label(container, text="Novo Cliente Rápido", font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg="#272f43")
        lbl_t.pack(anchor="w", pady=(0, 16))

        # Nome
        self._field(container, "Nome / Razão Social *", self.var_nome)
        # CPF/CNPJ
        self._field(container, "CPF / CNPJ *", self.var_cpf)
        # Celular
        self._field(container, "Celular / WhatsApp", self.var_cel)

        # Cidade e UF
        row = tk.Frame(container, bg="#272f43")
        row.pack(fill="x", pady=6)
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=1)

        f_cid = tk.Frame(row, bg="#272f43")
        f_cid.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Label(f_cid, text="Cidade", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#272f43").pack(anchor="w", pady=(0, 4))
        tk.Entry(f_cid, textvariable=self.var_cidade, bg="#1c2230", fg="white", insertbackground="white", bd=1, highlightbackground="#2a3245", font=("Segoe UI", 10)).pack(fill="x")

        f_uf = tk.Frame(row, bg="#272f43")
        f_uf.grid(row=0, column=1, sticky="ew")
        tk.Label(f_uf, text="UF", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#272f43").pack(anchor="w", pady=(0, 4))
        om = tk.OptionMenu(f_uf, self.var_uf, *ESTADOS_BRASIL)
        om.config(bg="#1c2230", fg="white", activebackground="#4f77ff", bd=1, highlightthickness=0, font=("Segoe UI", 10))
        om["menu"].config(bg="#1c2230", fg="white")
        om.pack(fill="x")

        # Botões
        btn_bar = tk.Frame(container, bg="#272f43")
        btn_bar.pack(fill="x", side="bottom", pady=(16, 0))

        tk.Button(btn_bar, text="Cancelar", font=("Segoe UI", 10, "bold"), fg="#9ca3af", bg="#1c2230", bd=0, padx=16, pady=8, cursor="hand2", command=self.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_bar, text="Salvar e Selecionar", font=("Segoe UI", 10, "bold"), fg="white", bg="#10b981", activebackground="#059669", bd=0, padx=20, pady=8, cursor="hand2", command=self._confirm).pack(side="right")

    def _field(self, parent, label, var):
        f = tk.Frame(parent, bg="#272f43")
        f.pack(fill="x", pady=6)
        tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#272f43").pack(anchor="w", pady=(0, 4))
        tk.Entry(f, textvariable=var, bg="#1c2230", fg="white", insertbackground="white", bd=1, highlightbackground="#2a3245", font=("Segoe UI", 10)).pack(fill="x")

    def _confirm(self):
        nome = self.var_nome.get().strip()
        cpf = self.var_cpf.get().strip()
        if not nome or not cpf:
            messagebox.showwarning("Aviso", "Preencha Nome e CPF/CNPJ.")
            return

        new_client = ClientService.save_client({
            "nome": nome,
            "cpf_cnpj": cpf,
            "celular": self.var_cel.get().strip(),
            "cidade": self.var_cidade.get().strip() or "São Paulo",
            "uf": self.var_uf.get(),
            "email": "contato@cliente.com"
        })
        self.on_save(new_client)
        self.destroy()


class TrucksFinalizarView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#1c2230")
        self.router = router
        self.kwargs = kwargs or {}

        # Unidades da Composição (Padrão 2 Unidades: Cavalo + Semirreboque)
        self.composition_units = self.kwargs.get("units_data", [
            {"id": 1, "type": "Cavalo Mecânico", "model": "VOLVO FH 540"},
            {"id": 2, "type": "Semirreboque", "model": "Randon 3 Eixos"}
        ])

        # Estado do Cliente Selecionado
        self.selected_client: Optional[Dict[str, Any]] = ClientService.get_client_by_id(1)

        # Variáveis dos Veículos (Placa e KM)
        self.unit_vars = []
        for u in self.composition_units:
            v_placa = tk.StringVar(value="ABC1D23" if u["id"] == 1 else "DEF5678")
            v_km = tk.StringVar(value="245000" if u["id"] == 1 else "120000")
            v_placa.trace_add("write", lambda *args, v=v_placa: self._mask_placa(v))
            self.unit_vars.append({"placa": v_placa, "km": v_km})

        # Busca de Cliente
        self.var_client_search = tk.StringVar()

        # Dados do Serviço
        self.var_tecnico = tk.StringVar(value=TECNICOS_LISTA[0])

        # Ícones
        self.img_truck = create_icon_image("truck", size=18, color="#60a5fa")
        self.img_user = create_icon_image("user", size=18, color="#10b981")
        self.img_clip = create_icon_image("clipboard_list", size=18, color="#c084fc")
        self.img_search = create_icon_image("search", size=16, color="#8a94a6")
        self.img_plus = create_icon_image("plus", size=16, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # 1. AlignmentHeader
        self.header = AlignmentHeader(
            self,
            title="Finalizar Alinhamento",
            subtitle="Preencha as placas, vincule o proprietário e gere o relatório",
            on_back=lambda: self.router.navigate("trucks.medidas"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # 2. Container Rolável Central (<main> max-w-4xl)
        self.scroll_canvas = tk.Canvas(self, bg="#1c2230", highlightthickness=0, bd=0)
        self.scroll_canvas.pack(fill="both", expand=True, padx=24, pady=16)

        self.scroll_inner = tk.Frame(self.scroll_canvas, bg="#1c2230")
        self.scroll_canvas.create_window((0, 0), window=self.scroll_inner, anchor="nw")

        self.scroll_canvas.bind("<Configure>", lambda e: self.scroll_canvas.itemconfig(self.scroll_canvas.find_withtag("all")[0], width=e.width))
        self.scroll_inner.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        setup_canvas_scrolling(self.scroll_canvas, self.scroll_inner)

        # Box Central max-w-4xl
        self.center_box = tk.Frame(self.scroll_inner, bg="#1c2230")
        self.center_box.pack(anchor="n", fill="x", padx=40)

        # ==========================================
        # CARD 1: VEÍCULOS DA COMPOSIÇÃO
        # ==========================================
        card1 = tk.Frame(self.center_box, bg="#272f43", highlightbackground="#2a3245", highlightthickness=1, padx=24, pady=20)
        card1.pack(fill="x", pady=(0, 20))

        hdr1 = tk.Frame(card1, bg="#272f43")
        hdr1.pack(fill="x", pady=(0, 16))
        tk.Label(hdr1, image=self.img_truck, bg="#272f43").pack(side="left", padx=(0, 8))
        tk.Label(hdr1, text="1. Veículos da Composição", font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#272f43").pack(side="left")

        for idx, unit in enumerate(self.composition_units):
            u_box = tk.Frame(card1, bg="#1c2230", highlightbackground="#2a3245", highlightthickness=1, padx=16, pady=14)
            u_box.pack(fill="x", pady=6)

            title_str = f"UNIDADE {unit['id']} — {unit['type'].upper()} ({unit.get('model', 'Padrão')})"
            tk.Label(u_box, text=title_str, font=("Segoe UI", 9, "bold"), fg="#60a5fa", bg="#1c2230").pack(anchor="w", pady=(0, 8))

            f_row = tk.Frame(u_box, bg="#1c2230")
            f_row.pack(fill="x")
            f_row.grid_columnconfigure(0, weight=1)
            f_row.grid_columnconfigure(1, weight=1)

            # Placa
            f_p = tk.Frame(f_row, bg="#1c2230")
            f_p.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            tk.Label(f_p, text="Placa do Veículo *", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1c2230").pack(anchor="w", pady=(0, 4))
            tk.Entry(f_p, textvariable=self.unit_vars[idx]["placa"], font=("Consolas", 11, "bold"), fg="#60a5fa", bg="#0d1117", insertbackground="white", bd=1, highlightbackground="#2a3245").pack(fill="x")

            # KM Rodado
            f_k = tk.Frame(f_row, bg="#1c2230")
            f_k.grid(row=0, column=1, sticky="ew", padx=(8, 0))
            tk.Label(f_k, text="Quilometragem (KM) *", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#1c2230").pack(anchor="w", pady=(0, 4))
            tk.Entry(f_k, textvariable=self.unit_vars[idx]["km"], font=("Segoe UI", 10, "bold"), fg="#FFFFFF", bg="#0d1117", insertbackground="white", bd=1, highlightbackground="#2a3245").pack(fill="x")

        # ==========================================
        # CARD 2: PROPRIETÁRIO / CLIENTE
        # ==========================================
        self.card2 = tk.Frame(self.center_box, bg="#272f43", highlightbackground="#2a3245", highlightthickness=1, padx=24, pady=20)
        self.card2.pack(fill="x", pady=(0, 20))

        hdr2 = tk.Frame(self.card2, bg="#272f43")
        hdr2.pack(fill="x", pady=(0, 16))
        tk.Label(hdr2, image=self.img_user, bg="#272f43").pack(side="left", padx=(0, 8))
        tk.Label(hdr2, text="2. Proprietário / Cliente", font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#272f43").pack(side="left")

        self.client_body_frame = tk.Frame(self.card2, bg="#272f43")
        self.client_body_frame.pack(fill="x")

        self._render_client_state()

        # ==========================================
        # CARD 3: DADOS DO SERVIÇO
        # ==========================================
        card3 = tk.Frame(self.center_box, bg="#272f43", highlightbackground="#2a3245", highlightthickness=1, padx=24, pady=20)
        card3.pack(fill="x", pady=(0, 20))

        hdr3 = tk.Frame(card3, bg="#272f43")
        hdr3.pack(fill="x", pady=(0, 16))
        tk.Label(hdr3, image=self.img_clip, bg="#272f43").pack(side="left", padx=(0, 8))
        tk.Label(hdr3, text="3. Dados do Serviço & Técnico", font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#272f43").pack(side="left")

        # Técnico Responsável
        f_tec = tk.Frame(card3, bg="#272f43")
        f_tec.pack(fill="x", pady=(0, 12))
        tk.Label(f_tec, text="Técnico Responsável pelo Alinhamento *", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#272f43").pack(anchor="w", pady=(0, 4))
        om_tec = tk.OptionMenu(f_tec, self.var_tecnico, *TECNICOS_LISTA)
        om_tec.config(bg="#0d1117", fg="white", activebackground="#2563eb", bd=1, highlightbackground="#2a3245", font=("Segoe UI", 10))
        om_tec["menu"].config(bg="#1c2230", fg="white")
        om_tec.pack(fill="x")

        # Observações Técnicas
        f_obs = tk.Frame(card3, bg="#272f43")
        f_obs.pack(fill="x")
        tk.Label(f_obs, text="Observações Técnicas Adicionais", font=("Segoe UI", 9, "bold"), fg="#d1d5db", bg="#272f43").pack(anchor="w", pady=(0, 4))
        self.txt_obs = tk.Text(f_obs, height=4, bg="#0d1117", fg="white", insertbackground="white", bd=1, highlightbackground="#2a3245", font=("Segoe UI", 10))
        self.txt_obs.pack(fill="x")
        self.txt_obs.insert("1.0", "Alinhamento e geometria dos eixos realizados conforme especificações de fábrica.")

        # ==========================================
        # BOTÕES DE AÇÃO DO FORMULÁRIO
        # ==========================================
        btn_bar = tk.Frame(self.center_box, bg="#1c2230")
        btn_bar.pack(fill="x", pady=(10, 32))

        btn_cancel = tk.Button(
            btn_bar,
            text="Voltar",
            font=("Segoe UI", 10, "bold"),
            fg="#9ca3af",
            bg="#1c2230",
            activebackground="#2a3245",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self.router.navigate("trucks.medidas")
        )
        btn_cancel.pack(side="left")

        btn_submit = tk.Button(
            btn_bar,
            text="  GERAR RELATÓRIO PDF  ",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#10b981",
            activebackground="#059669",
            bd=0,
            padx=32,
            pady=12,
            cursor="hand2",
            command=self._submit_finalization
        )
        btn_submit.pack(side="right")

        # Atualizar a região de rolagem do Canvas
        self.scroll_inner.update_idletasks()
        self.scroll_canvas.config(scrollregion=(0, 0, self.scroll_inner.winfo_width(), self.scroll_inner.winfo_height()))

    def _render_client_state(self):
        for child in self.client_body_frame.winfo_children():
            child.destroy()

        if self.selected_client:
            # ESTADO: CLIENTE SELECIONADO (Card de destaque #1c2230 com borda azul)
            c = self.selected_client
            card_c = tk.Frame(self.client_body_frame, bg="#1c2230", highlightbackground="#2563eb", highlightthickness=1, padx=20, pady=16)
            card_c.pack(fill="x")

            top_line = tk.Frame(card_c, bg="#1c2230")
            top_line.pack(fill="x")

            lbl_name = tk.Label(top_line, text=c["nome"], font=("Segoe UI", 14, "bold"), fg="#FFFFFF", bg="#1c2230")
            lbl_name.pack(side="left")

            btn_change = tk.Button(
                top_line,
                text="Alterar Cliente",
                font=("Segoe UI", 9, "bold"),
                fg="#f87171",
                bg="#2a1820",
                activebackground="#3d1d28",
                bd=1,
                highlightbackground="#ef4444",
                padx=10,
                pady=3,
                cursor="hand2",
                command=self._clear_selected_client
            )
            btn_change.pack(side="right")

            sub_info = f"CPF/CNPJ: {c['cpf_cnpj']}   •   Celular: {c.get('celular', '(11) 98765-4321')}   •   {c.get('cidade', 'São Paulo')} - {c.get('uf', 'SP')}"
            lbl_sub = tk.Label(card_c, text=sub_info, font=("Segoe UI", 9), fg="#9ca3af", bg="#1c2230")
            lbl_sub.pack(anchor="w", pady=(6, 0))

        else:
            # ESTADO: BUSCA EM TEMPO REAL
            search_row = tk.Frame(self.client_body_frame, bg="#272f43")
            search_row.pack(fill="x")

            box_input = tk.Frame(search_row, bg="#1c2230", highlightbackground="#2a3245", highlightthickness=1, padx=10, pady=6)
            box_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

            tk.Label(box_input, image=self.img_search, bg="#1c2230").pack(side="left", padx=(0, 8))
            entry_s = tk.Entry(box_input, textvariable=self.var_client_search, bg="#1c2230", fg="white", insertbackground="white", bd=0, font=("Segoe UI", 10))
            entry_s.pack(side="left", fill="x", expand=True)

            btn_search = tk.Button(
                search_row,
                text="Buscar",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#2563eb",
                activebackground="#1d4ed8",
                bd=0,
                padx=16,
                pady=8,
                cursor="hand2",
                command=self._do_search_client
            )
            btn_search.pack(side="left", padx=(0, 8))

            btn_quick_new = tk.Button(
                search_row,
                text=" + Novo ",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#10b981",
                activebackground="#059669",
                bd=0,
                padx=16,
                pady=8,
                cursor="hand2",
                command=self._open_quick_client_modal
            )
            btn_quick_new.pack(side="left")

    def _do_search_client(self):
        query = self.var_client_search.get().strip()
        results = ClientService.filter_clients(nome_filter=query)
        if results:
            self.selected_client = results[0]
            self._render_client_state()
        else:
            messagebox.showinfo("Busca de Cliente", f"Nenhum cliente encontrado com a busca '{query}'. Clique em '+ Novo' para cadastrar.")

    def _clear_selected_client(self):
        self.selected_client = None
        self._render_client_state()

    def _open_quick_client_modal(self):
        QuickClientDialog(self, on_save=self._on_quick_client_saved)

    def _on_quick_client_saved(self, client: Dict[str, Any]):
        self.selected_client = client
        self._render_client_state()

    def _mask_placa(self, var: tk.StringVar):
        raw = "".join(filter(str.isalnum, var.get())).upper()[:7]
        if var.get() != raw:
            var.set(raw)

    def _submit_finalization(self):
        if not self.selected_client:
            messagebox.showwarning("Aviso", "Por favor selecione ou cadastre o Proprietário / Cliente.")
            return

        final_data = {
            "client": self.selected_client,
            "tecnico": self.var_tecnico.get(),
            "observacoes": self.txt_obs.get("1.0", tk.END).strip(),
            "alignment_mode": getattr(self, "alignment_mode", "MANUAL"),
            "units": [
                {
                    "type": self.composition_units[idx]["type"],
                    "model": self.composition_units[idx].get("model", "Padrão"),
                    "placa": self.unit_vars[idx]["placa"].get(),
                    "km": self.unit_vars[idx]["km"].get()
                }
                for idx in range(len(self.composition_units))
            ]
        }

        # Avança para a Tela 2: Prévia e Ações do PDF (preview.py)
        self.router.navigate("trucks.preview", final_data=final_data)
