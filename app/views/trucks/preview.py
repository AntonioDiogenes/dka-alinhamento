"""
Tela 2 das Etapas Finais: Prévia e Ações do Relatório PDF (views/trucks/preview.py).
Visualização em 2 Colunas:
- Coluna Esquerda: Visualizador de PDF em Tempo Real (Folha de Relatório e Certificado de Alinhamento).
  Tabelas internas reconstruídas sob um único grid uniforme (uniform grid columns) para garantir 100% de alinhamento vertical reto.
- Coluna Direita: Painel Lateral de Ações:
  1. ABRIR O PDF (Abre o relatório gerado no leitor/navegador do SO).
  2. CONCLUIR ATENDIMENTO (Gera/salva o PDF, grava a Ordem de Serviço no banco de dados SQLCipher e redireciona para a listagem de histórico de atendimentos).
  3. VOLTAR (Retorna ao formulário de finalização).
"""
import os
import webbrowser
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Dict, Any

from app.config.settings import COLORS
from app.components.alignment_header import AlignmentHeader
from app.utils.icons import create_icon_image
from app.utils.pdf_generator import generate_alignment_pdf, get_downloads_directory
from app.services.attendance_service import AttendanceService

class TrucksPreviewView(tk.Frame):
    def __init__(self, parent: tk.Widget, router, kwargs=None):
        super().__init__(parent, bg="#111520")
        self.router = router
        self.kwargs = kwargs or {}

        # Dados da Finalização
        self.final_data = self.kwargs.get("final_data", {
            "client": {"nome": "Logística TransBrasil Ltda", "cpf_cnpj": "12.345.678/0001-90", "cidade": "São Paulo", "uf": "SP"},
            "tecnico": "Carlos Eduardo - Mecânico Chefe",
            "observacoes": "Alinhamento e geometria dos eixos realizados conforme especificações de fábrica.",
            "units": [
                {"type": "Cavalo Mecânico", "model": "VOLVO FH 540", "placa": "ABC1D23", "km": "245000"},
                {"type": "Semirreboque", "model": "Randon 3 Eixos", "placa": "DEF5678", "km": "120000"}
            ]
        })

        # Ícones
        self.img_file = create_icon_image("file_text", size=20, color="#60a5fa")
        self.img_eye = create_icon_image("eye", size=18, color="#FFFFFF")
        self.img_check = create_icon_image("check", size=18, color="#FFFFFF")
        self.img_back = create_icon_image("arrow_left", size=18, color="#FFFFFF")

        self._build_ui()

    def _build_ui(self):
        # 1. AlignmentHeader
        self.header = AlignmentHeader(
            self,
            title="Prévia do Relatório PDF",
            subtitle="Certificado de Alinhamento Técnico  •  OS #1043",
            on_back=lambda: self.router.navigate("trucks.finalizar"),
            on_close=lambda: self.router.navigate("dashboard")
        )
        self.header.pack(fill="x", side="top")

        # 2. Split Area (Visualizador de PDF + Painel Lateral de Ações)
        split_area = tk.Frame(self, bg="#111520")
        split_area.pack(fill="both", expand=True)

        split_area.grid_columnconfigure(0, weight=1) # Esquerda: PDF (Expand)
        split_area.grid_columnconfigure(1, weight=0) # Direita: Painel w-80 (320px)
        split_area.grid_rowconfigure(0, weight=1)

        # ------------------------------------------
        # COLUNA ESQUERDA: VISUALIZADOR DE PDF EM TEMPO REAL
        # ------------------------------------------
        left_col = tk.Frame(split_area, bg="#111520", padx=24, pady=20)
        left_col.grid(row=0, column=0, sticky="nsew")

        # Cabeçalho da Prévia
        prev_hdr = tk.Frame(left_col, bg="#111520")
        prev_hdr.pack(fill="x", pady=(0, 12))

        tk.Label(prev_hdr, image=self.img_file, bg="#111520").pack(side="left", padx=(0, 8))
        tk.Label(prev_hdr, text="Prévia da Folha do Relatório de Alinhamento", font=("Segoe UI", 11, "bold"), fg="#FFFFFF", bg="#111520").pack(side="left")

        # Canvas/Frame da Folha do PDF Embutida (Fundo Branco Simulado #ffffff)
        pdf_canvas = tk.Canvas(left_col, bg="#111520", highlightthickness=0, bd=0)
        pdf_canvas.pack(fill="both", expand=True)

        sheet = tk.Frame(pdf_canvas, bg="#ffffff", padx=32, pady=28, highlightbackground="#e2e8f0", highlightthickness=1)
        pdf_canvas.create_window((0, 0), window=sheet, anchor="nw")
        pdf_canvas.bind("<Configure>", lambda e: pdf_canvas.itemconfig(pdf_canvas.find_withtag("all")[0], width=e.width))

        # CONTEÚDO IMPRESSO DO PDF
        client = self.final_data["client"]
        client_name = client["nome"] if isinstance(client, dict) else str(client)
        client_doc = client.get("cpf_cnpj", "12.345.678/0001-90") if isinstance(client, dict) else ""
        cidade_uf = f"{client.get('cidade', 'São Paulo')} - {client.get('uf', 'SP')}" if isinstance(client, dict) else ""

        units = self.final_data["units"]

        # Cabeçalho do Documento
        sheet_hdr = tk.Frame(sheet, bg="#ffffff")
        sheet_hdr.pack(fill="x", pady=(0, 16))

        tk.Label(sheet_hdr, text="CENTRO AUTOMOTIVO & OFICINA TRUCK", font=("Segoe UI", 14, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w")
        tk.Label(sheet_hdr, text="Relatório Técnico de Alinhamento e Geometria Veicular — OS #1043", font=("Segoe UI", 10, "bold"), fg="#2563eb", bg="#ffffff").pack(anchor="w")
        tk.Frame(sheet, bg="#0f172a", height=2).pack(fill="x", pady=(0, 16))

        # Seção 1: Dados do Cliente e Serviço
        s1 = tk.Frame(sheet, bg="#f8fafc", highlightbackground="#e2e8f0", highlightthickness=1, padx=16, pady=12)
        s1.pack(fill="x", pady=(0, 16))

        tk.Label(s1, text=f"CLIENTE: {client_name}   |   CPF/CNPJ: {client_doc}", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#f8fafc").pack(anchor="w")
        tk.Label(s1, text=f"LOCALIDADE: {cidade_uf}   |   TÉCNICO: {self.final_data['tecnico']}", font=("Segoe UI", 9), fg="#475569", bg="#f8fafc").pack(anchor="w", pady=(2, 0))

        # Seção 2: Tabela de Veículos da Composição (Grid Unificado com Colunas Retas)
        tk.Label(sheet, text="COMPOSIÇÃO VEICULAR", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", pady=(0, 6))

        tbl_v = tk.Frame(sheet, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1)
        tbl_v.pack(fill="x", pady=(0, 16))

        tbl_v.grid_columnconfigure(0, weight=2, uniform="tbl_v_col")
        tbl_v.grid_columnconfigure(1, weight=3, uniform="tbl_v_col")
        tbl_v.grid_columnconfigure(2, weight=2, uniform="tbl_v_col")
        tbl_v.grid_columnconfigure(3, weight=2, uniform="tbl_v_col")

        # Row 0: Header da tabela
        th_bg = "#f1f5f9"
        tk.Label(tbl_v, text="Unidade", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_v, text="Modelo", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_v, text="Placa", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_v, text="KM Rodado", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=12, pady=6)

        for u_idx, u in enumerate(units, start=1):
            tk.Label(tbl_v, text=u["type"], font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff", anchor="w").grid(row=u_idx, column=0, sticky="ew", padx=12, pady=6)
            tk.Label(tbl_v, text=u.get("model", "Padrão"), font=("Segoe UI", 9), fg="#334155", bg="#ffffff", anchor="w").grid(row=u_idx, column=1, sticky="ew", padx=12, pady=6)
            tk.Label(tbl_v, text=u["placa"], font=("Consolas", 9, "bold"), fg="#2563eb", bg="#ffffff", anchor="w").grid(row=u_idx, column=2, sticky="ew", padx=12, pady=6)
            tk.Label(tbl_v, text=f"{u['km']} km", font=("Segoe UI", 9), fg="#334155", bg="#ffffff", anchor="w").grid(row=u_idx, column=3, sticky="ew", padx=12, pady=6)

        # Seção 3: Tabela de Geometria dos Eixos (Grid Unificado com Colunas Retas)
        tk.Label(sheet, text="RESULTADO DA MEDIÇÃO E GEOMETRIA DOS EIXOS", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", pady=(0, 6))

        tbl_g = tk.Frame(sheet, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1)
        tbl_g.pack(fill="x", pady=(0, 16))

        tbl_g.grid_columnconfigure(0, weight=3, uniform="tbl_g_col")
        tbl_g.grid_columnconfigure(1, weight=2, uniform="tbl_g_col")
        tbl_g.grid_columnconfigure(2, weight=2, uniform="tbl_g_col")
        tbl_g.grid_columnconfigure(3, weight=2, uniform="tbl_g_col")

        # Row 0: Header
        tk.Label(tbl_g, text="Parâmetro", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_g, text="Inicial (Antes)", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_g, text="Final (Depois)", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=12, pady=6)
        tk.Label(tbl_g, text="Status Tolerância", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg=th_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=12, pady=6)

        geom_items = [
            ("Convergência Dianteira Esq", "+0,75 mm", "+0,65 mm", "OK (Aprovado)", "#10b981"),
            ("Convergência Dianteira Dir", "+0,75 mm", "+0,65 mm", "OK (Aprovado)", "#10b981"),
            ("Camber Dianteiro Esq", "+0,20°", "+0,15°", "OK (Aprovado)", "#10b981"),
            ("Caster Dianteiro Esq", "+2,50°", "+2,60°", "OK (Aprovado)", "#10b981"),
            ("Convergência Traseira Total", "+1,00 mm", "+0,80 mm", "OK (Aprovado)", "#10b981")
        ]

        for g_idx, (p_name, p_init, p_fin, p_st, p_col) in enumerate(geom_items, start=1):
            tk.Label(tbl_g, text=p_name, font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff", anchor="w").grid(row=g_idx, column=0, sticky="ew", padx=12, pady=5)
            tk.Label(tbl_g, text=p_init, font=("Segoe UI", 9), fg="#dc2626", bg="#ffffff", anchor="w").grid(row=g_idx, column=1, sticky="ew", padx=12, pady=5)
            tk.Label(tbl_g, text=p_fin, font=("Segoe UI", 9, "bold"), fg="#16a34a", bg="#ffffff", anchor="w").grid(row=g_idx, column=2, sticky="ew", padx=12, pady=5)

            st_box = tk.Frame(tbl_g, bg="#ffffff")
            st_box.grid(row=g_idx, column=3, sticky="w", padx=12, pady=5)
            tk.Label(st_box, text=p_st, font=("Segoe UI", 8, "bold"), fg="white", bg=p_col, padx=6, pady=1).pack(side="left")

        # Campo de Assinatura
        sig_box = tk.Frame(sheet, bg="#ffffff")
        sig_box.pack(fill="x", pady=(20, 0))

        tk.Frame(sig_box, bg="#0f172a", height=1, width=220).pack(anchor="e", pady=(0, 4))
        tk.Label(sig_box, text=f"Assinatura do Técnico: {self.final_data['tecnico']}", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="e")

        # ------------------------------------------
        # COLUNA DIREITA: PAINEL LATERAL DE AÇÕES (w-80 / 320px)
        # ------------------------------------------
        right_panel = tk.Frame(
            split_area,
            bg="#161a26",
            width=320,
            highlightbackground="#2a3245",
            highlightthickness=1,
            padx=20,
            pady=28
        )
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.pack_propagate(False)

        lbl_panel_title = tk.Label(right_panel, text="AÇÕES DO RELATÓRIO", font=("Segoe UI", 9, "bold"), fg="#9ca3af", bg="#161a26")
        lbl_panel_title.pack(anchor="w", pady=(0, 16))

        # 1. BOTÃO ABRIR O PDF (bg-blue-600)
        btn_open_pdf = tk.Button(
            right_panel,
            text=" ABRIR O PDF ",
            image=self.img_eye,
            compound="left",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            bd=0,
            padx=16,
            pady=14,
            cursor="hand2",
            command=self._do_open_pdf
        )
        btn_open_pdf.pack(fill="x", pady=(0, 12))

        # 2. BOTÃO CONCLUIR ATENDIMENTO (bg-emerald-600 -> Salva PDF, Grava OS e navega para /attendances)
        btn_conclude = tk.Button(
            right_panel,
            text=" CONCLUIR ATENDIMENTO ",
            image=self.img_check,
            compound="left",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#10b981",
            activebackground="#059669",
            bd=0,
            padx=16,
            pady=14,
            cursor="hand2",
            command=self._do_conclude
        )
        btn_conclude.pack(fill="x", pady=(0, 12))

        # 3. BOTÃO VOLTAR (bg-transparent border)
        btn_back_form = tk.Button(
            right_panel,
            text=" VOLTAR ",
            image=self.img_back,
            compound="left",
            font=("Segoe UI", 9, "bold"),
            fg="white",
            bg="#161a26",
            activebackground="#2a3245",
            bd=1,
            highlightbackground="#2a3245",
            padx=16,
            pady=12,
            cursor="hand2",
            command=lambda: self.router.navigate("trucks.finalizar")
        )
        btn_back_form.pack(fill="x", side="bottom")

    def _do_open_pdf(self):
        """Gera o arquivo PDF e o abre no leitor/navegador padrão do sistema operacional."""
        try:
            pdf_path = generate_alignment_pdf(self.final_data)
            webbrowser.open(f"file://{pdf_path}")
            messagebox.showinfo("Abrir PDF", f"Relatório PDF gerado e aberto com sucesso:\n\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir PDF", f"Não foi possível abrir o relatório PDF: {e}")

    def _do_conclude(self):
        """Salva o arquivo PDF, grava o atendimento no banco SQLCipher e redireciona para a listagem de histórico."""
        try:
            pdf_path = generate_alignment_pdf(self.final_data)

            client_info = self.final_data.get("client", {})
            if isinstance(client_info, dict):
                client_name = client_info.get("nome", "Cliente")
            else:
                client_name = str(client_info)

            units = self.final_data.get("units", [])
            main_unit = units[0] if units else {}
            model_name = main_unit.get("model", "Volvo FH 540")
            plate_name = main_unit.get("placa", "ABC-1D23")

            now = datetime.now()
            date_formatted = now.strftime("%d/%m/%Y %H:%M")
            date_iso = now.strftime("%Y-%m-%d")

            # Persistir o atendimento no banco SQLCipher via AttendanceService
            new_att = AttendanceService.create_attendance({
                "date_formatted": date_formatted,
                "date_iso": date_iso,
                "model": model_name,
                "plate": plate_name,
                "client": client_name,
                "pdf_url": f"file://{pdf_path}"
            })

            os_id = new_att.get("id", 1043)
            messagebox.showinfo(
                "Atendimento Concluído",
                f"Ordem de serviço OS #{os_id} (Placa: {plate_name}) finalizada e salva com sucesso no banco de dados!"
            )

            # Redirecionar diretamente para o Histórico de Atendimentos (/attendances)
            self.router.navigate("attendances")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar Atendimento", f"Ocorreu uma falha ao salvar o atendimento no banco de dados: {e}")
