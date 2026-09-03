"""
Formulário Reutilizável de Cliente (components/client_form.py).
Dividido nas 3 seções especificadas: Dados Básicos, Endereço e Informações Adicionais.
Suporta o modo Somente Leitura (readOnly=True) para a tela de visualização.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, Optional

ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

class ClientForm(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        client_data: Optional[Dict[str, Any]] = None,
        read_only: bool = False,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        bg_color = "#1a1f2e"
        fg_color = "#ffffff"
        border_color = "#2a3245"

        super().__init__(
            parent,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=24,
            pady=24,
            **kwargs
        )

        self.client_data = client_data or {}
        self.read_only = read_only
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.input_bg = "#0d1117"
        self.input_fg = "#ffffff"
        self.muted_fg = "#9ca3af"

        # Variáveis de formulário
        self.var_nome = tk.StringVar(value=self.client_data.get("nome", ""))
        self.var_cpf_cnpj = tk.StringVar(value=self.client_data.get("cpf_cnpj", ""))
        self.var_email = tk.StringVar(value=self.client_data.get("email", ""))
        self.var_celular = tk.StringVar(value=self.client_data.get("celular", ""))
        self.var_telefone = tk.StringVar(value=self.client_data.get("telefone_fixo", ""))

        self.var_cep = tk.StringVar(value=self.client_data.get("cep", ""))
        self.var_logradouro = tk.StringVar(value=self.client_data.get("logradouro", ""))
        self.var_numero = tk.StringVar(value=self.client_data.get("numero", ""))
        self.var_complemento = tk.StringVar(value=self.client_data.get("complemento", ""))
        self.var_bairro = tk.StringVar(value=self.client_data.get("bairro", ""))
        self.var_cidade = tk.StringVar(value=self.client_data.get("cidade", ""))
        self.var_uf = tk.StringVar(value=self.client_data.get("uf", "SP"))

        self.var_ativo = tk.BooleanVar(value=self.client_data.get("ativo", True))

        # Formatação dinâmica de máscara CPF/CNPJ
        self.var_cpf_cnpj.trace_add("write", self._mask_cpf_cnpj)
        self.var_celular.trace_add("write", self._mask_celular)

        self._build_form()

    def _build_form(self):
        """Monta o formulário nas 3 seções demarcadas."""
        # ==========================================
        # SEÇÃO 1: DADOS BÁSICOS
        # ==========================================
        self._build_section_header("1. Dados Básicos")

        sec1 = tk.Frame(self, bg=self.bg_color)
        sec1.pack(fill="x", pady=(0, 20))
        sec1.grid_columnconfigure(0, weight=1)
        sec1.grid_columnconfigure(1, weight=1)
        sec1.grid_columnconfigure(2, weight=1)

        self._create_field(sec1, "Nome / Razão Social *", self.var_nome, row=0, col=0, colspan=2)
        self._create_field(sec1, "CPF / CNPJ *", self.var_cpf_cnpj, row=0, col=2, colspan=1)

        self._create_field(sec1, "E-mail", self.var_email, row=1, col=0)
        self._create_field(sec1, "Celular / WhatsApp", self.var_celular, row=1, col=1)
        self._create_field(sec1, "Telefone Fixo", self.var_telefone, row=1, col=2)

        # ==========================================
        # SEÇÃO 2: ENDEREÇO
        # ==========================================
        self._build_section_header("2. Endereço")

        sec2 = tk.Frame(self, bg=self.bg_color)
        sec2.pack(fill="x", pady=(0, 20))
        sec2.grid_columnconfigure(0, weight=1)
        sec2.grid_columnconfigure(1, weight=2)
        sec2.grid_columnconfigure(2, weight=1)
        sec2.grid_columnconfigure(3, weight=1)

        self._create_field(sec2, "CEP", self.var_cep, row=0, col=0)
        self._create_field(sec2, "Logradouro", self.var_logradouro, row=0, col=1, colspan=2)
        self._create_field(sec2, "Número", self.var_numero, row=0, col=3)

        self._create_field(sec2, "Complemento", self.var_complemento, row=1, col=0)
        self._create_field(sec2, "Bairro", self.var_bairro, row=1, col=1)
        self._create_field(sec2, "Cidade", self.var_cidade, row=1, col=2)

        # UF Dropdown
        uf_frame = tk.Frame(sec2, bg=self.bg_color)
        uf_frame.grid(row=1, column=3, sticky="ew", padx=8, pady=6)

        lbl_uf = tk.Label(uf_frame, text="UF", font=("Segoe UI", 9, "bold"), fg=self.fg_color, bg=self.bg_color)
        lbl_uf.pack(anchor="w", pady=(0, 4))

        om_uf = tk.OptionMenu(uf_frame, self.var_uf, *ESTADOS_BRASIL)
        om_uf.config(
            bg=self.input_bg,
            fg=self.input_fg,
            activebackground="#4f77ff",
            activeforeground="white",
            bd=1,
            highlightthickness=0,
            font=("Segoe UI", 10),
            state="disabled" if self.read_only else "normal"
        )
        om_uf["menu"].config(bg="#1c2230", fg="white", activebackground="#4f77ff")
        om_uf.pack(fill="x")

        # ==========================================
        # SEÇÃO 3: INFORMAÇÕES ADICIONAIS
        # ==========================================
        self._build_section_header("3. Informações Adicionais")

        sec3 = tk.Frame(self, bg=self.bg_color)
        sec3.pack(fill="x", pady=(0, 20))

        lbl_obs = tk.Label(sec3, text="Observações Internas", font=("Segoe UI", 9, "bold"), fg=self.fg_color, bg=self.bg_color)
        lbl_obs.pack(anchor="w", pady=(0, 4))

        self.txt_obs = tk.Text(
            sec3,
            height=4,
            bg=self.input_bg,
            fg=self.input_fg,
            insertbackground="white",
            bd=1,
            highlightbackground="#2a3245",
            font=("Segoe UI", 10),
            state="disabled" if self.read_only else "normal"
        )
        self.txt_obs.pack(fill="x", pady=(0, 12))

        obs_val = self.client_data.get("observacoes", "")
        if obs_val:
            self.txt_obs.insert("1.0", obs_val)

        chk_ativo = tk.Checkbutton(
            sec3,
            text="Cliente Ativo no Sistema",
            variable=self.var_ativo,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.bg_color,
            selectcolor=self.input_bg,
            font=("Segoe UI", 10),
            state="disabled" if self.read_only else "normal"
        )
        chk_ativo.pack(anchor="w")

        # ==========================================
        # BOTÕES DE AÇÃO DO FORMULÁRIO
        # ==========================================
        self.btn_bar = tk.Frame(self, bg=self.bg_color)
        self.btn_bar.pack(fill="x", pady=(12, 0))

        cancel_text = "Voltar" if self.read_only else "Cancelar"
        btn_cancel = tk.Button(
            self.btn_bar,
            text=cancel_text,
            font=("Segoe UI", 10, "bold"),
            fg=self.fg_color,
            bg="#2a3245",
            activebackground="#3b465e",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._handle_cancel
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        if not self.read_only:
            save_label = "Atualizar Cliente" if self.client_data.get("id") else "Salvar Cliente"
            btn_save = tk.Button(
                self.btn_bar,
                text=save_label,
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#4f77ff",
                activebackground="#3b60ff",
                bd=0,
                padx=24,
                pady=8,
                cursor="hand2",
                command=self._handle_save
            )
            btn_save.pack(side="right")

    def _build_section_header(self, title: str):
        hdr = tk.Frame(self, bg=self.bg_color)
        hdr.pack(fill="x", pady=(12, 10))

        lbl = tk.Label(hdr, text=title, font=("Segoe UI", 11, "bold"), fg=self.fg_color, bg=self.bg_color)
        lbl.pack(anchor="w")

        divider = tk.Frame(hdr, bg="#2a3245", height=1)
        divider.pack(fill="x", pady=(4, 0))

    def _create_field(self, parent: tk.Frame, label_text: str, var: tk.StringVar, row: int, col: int, colspan: int = 1):
        field_frame = tk.Frame(parent, bg=self.bg_color)
        field_frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=8, pady=6)

        lbl = tk.Label(field_frame, text=label_text, font=("Segoe UI", 9, "bold"), fg=self.fg_color, bg=self.bg_color)
        lbl.pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            field_frame,
            textvariable=var,
            bg=self.input_bg,
            fg=self.input_fg,
            insertbackground="white",
            bd=1,
            relief="solid",
            highlightbackground="#2a3245",
            highlightthickness=1,
            font=("Segoe UI", 11),
            state="disabled" if self.read_only else "normal"
        )
        entry.pack(fill="x", ipady=6)

    def _mask_cpf_cnpj(self, *args):
        raw = "".join(filter(str.isdigit, self.var_cpf_cnpj.get()))[:14]
        if len(raw) <= 11:
            formatted = raw
            if len(raw) > 3:
                formatted = raw[:3] + "." + raw[3:]
            if len(raw) > 6:
                formatted = formatted[:7] + "." + raw[6:]
            if len(raw) > 9:
                formatted = formatted[:11] + "-" + raw[9:]
        else:
            formatted = raw[:2] + "." + raw[2:5] + "." + raw[5:8] + "/" + raw[8:12] + "-" + raw[12:]

        if self.var_cpf_cnpj.get() != formatted:
            self.var_cpf_cnpj.set(formatted)

    def _mask_celular(self, *args):
        raw = "".join(filter(str.isdigit, self.var_celular.get()))[:11]
        formatted = raw
        if len(raw) > 0:
            formatted = "(" + raw
        if len(raw) > 2:
            formatted = "(" + raw[:2] + ") " + raw[2:]
        if len(raw) > 7:
            formatted = "(" + raw[:2] + ") " + raw[2:7] + "-" + raw[7:]

        if self.var_celular.get() != formatted:
            self.var_celular.set(formatted)

    def _handle_save(self):
        nome = self.var_nome.get().strip()
        cpf_cnpj = self.var_cpf_cnpj.get().strip()

        if not nome or not cpf_cnpj:
            messagebox.showwarning("Campos Obrigatórios", "Por favor preencha Nome e CPF/CNPJ.")
            return

        obs_content = self.txt_obs.get("1.0", tk.END).strip()

        data = {
            "id": self.client_data.get("id"),
            "nome": nome,
            "cpf_cnpj": cpf_cnpj,
            "email": self.var_email.get().strip(),
            "celular": self.var_celular.get().strip(),
            "telefone_fixo": self.var_telefone.get().strip(),
            "cep": self.var_cep.get().strip(),
            "logradouro": self.var_logradouro.get().strip(),
            "numero": self.var_numero.get().strip(),
            "complemento": self.var_complemento.get().strip(),
            "bairro": self.var_bairro.get().strip(),
            "cidade": self.var_cidade.get().strip(),
            "uf": self.var_uf.get(),
            "observacoes": obs_content,
            "ativo": self.var_ativo.get(),
        }

        if self.on_save:
            self.on_save(data)

    def _handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
