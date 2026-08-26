"""
Gerador Profissional de PDF de Relatório de Alinhamento (utils/pdf_generator.py).
Gera arquivos PDF formatados com ReportLab e os salva diretamente na pasta Downloads do usuário.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def get_downloads_directory() -> Path:
    """Retorna o caminho completo da pasta Downloads do usuário."""
    downloads_path = Path.home() / "Downloads"
    downloads_path.mkdir(parents=True, exist_ok=True)
    return downloads_path

def generate_alignment_pdf(final_data: Dict[str, Any], filename: str = "Relatorio_Alinhamento_OS1043.pdf") -> str:
    """Gera o arquivo PDF real formatado e o salva na pasta Downloads."""
    downloads_dir = get_downloads_directory()
    output_path = downloads_dir / filename

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos Customizados
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563eb")
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    normal_style = ParagraphStyle(
        "DocNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    bold_style = ParagraphStyle(
        "DocBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # 1. Cabeçalho do Documento
    story.append(Paragraph("CENTRO AUTOMOTIVO & OFICINA TRUCK", title_style))
    story.append(Paragraph("Relatório Técnico de Alinhamento e Geometria Veicular — OS #1043", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0f172a"), spaceAfter=12))

    # 2. Dados do Cliente e Serviço
    client = final_data.get("client", {})
    units = final_data.get("units", [])
    tecnico = final_data.get("tecnico", "Técnico Alinhador")
    obs = final_data.get("observacoes", "Alinhamento e geometria conforme normas do fabricante.")

    client_info = [
        [
            Paragraph(f"<b>CLIENTE:</b> {client.get('nome', 'N/A')}", normal_style),
            Paragraph(f"<b>CPF/CNPJ:</b> {client.get('cpf_cnpj', 'N/A')}", normal_style)
        ],
        [
            Paragraph(f"<b>LOCALIDADE:</b> {client.get('cidade', 'São Paulo')} - {client.get('uf', 'SP')}", normal_style),
            Paragraph(f"<b>TÉCNICO:</b> {tecnico}", normal_style)
        ]
    ]
    t_client = Table(client_info, colWidths=[270, 270])
    t_client.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_client)
    story.append(Spacer(1, 14))

    # 3. Composição Veicular (Tabela)
    story.append(Paragraph("COMPOSIÇÃO VEICULAR E QUILOMETRAGEM", section_style))

    comp_data = [
        [
            Paragraph("<b>Unidade</b>", bold_style),
            Paragraph("<b>Modelo</b>", bold_style),
            Paragraph("<b>Placa</b>", bold_style),
            Paragraph("<b>KM Rodado</b>", bold_style)
        ]
    ]

    for u in units:
        comp_data.append([
            Paragraph(u.get("type", "N/A"), normal_style),
            Paragraph(u.get("model", "Padrão"), normal_style),
            Paragraph(f"<b>{u.get('placa', 'ABC1D23')}</b>", normal_style),
            Paragraph(f"{u.get('km', '0')} km", normal_style)
        ])

    t_comp = Table(comp_data, colWidths=[135, 175, 115, 115])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 14))

    # 4. Tabela de Geometria dos Eixos (Medições)
    story.append(Paragraph("RESULTADO DAS MEDIÇÕES E GEOMETRIA DE EIXOS", section_style))

    geom_headers = [
        Paragraph("<b>Parâmetro</b>", bold_style),
        Paragraph("<b>Inicial (Antes)</b>", bold_style),
        Paragraph("<b>Final (Depois)</b>", bold_style),
        Paragraph("<b>Status Tolerância</b>", bold_style)
    ]

    geom_rows = [
        geom_headers,
        [Paragraph("Convergência Dianteira Esq", normal_style), Paragraph("+0,75 mm", normal_style), Paragraph("+0,65 mm", bold_style), Paragraph("<font color='#10b981'><b>OK (Aprovado)</b></font>", normal_style)],
        [Paragraph("Convergência Dianteira Dir", normal_style), Paragraph("+0,75 mm", normal_style), Paragraph("+0,65 mm", bold_style), Paragraph("<font color='#10b981'><b>OK (Aprovado)</b></font>", normal_style)],
        [Paragraph("Camber Dianteiro Esq", normal_style), Paragraph("+0,20°", normal_style), Paragraph("+0,15°", bold_style), Paragraph("<font color='#10b981'><b>OK (Aprovado)</b></font>", normal_style)],
        [Paragraph("Caster Dianteiro Esq", normal_style), Paragraph("+2,50°", normal_style), Paragraph("+2,60°", bold_style), Paragraph("<font color='#10b981'><b>OK (Aprovado)</b></font>", normal_style)],
        [Paragraph("Convergência Traseira Total", normal_style), Paragraph("+1,00 mm", normal_style), Paragraph("+0,80 mm", bold_style), Paragraph("<font color='#10b981'><b>OK (Aprovado)</b></font>", normal_style)],
    ]

    t_geom = Table(geom_rows, colWidths=[160, 120, 120, 140])
    t_geom.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_geom)
    story.append(Spacer(1, 14))

    # 5. Observações Técnicas
    if obs:
        story.append(Paragraph("OBSERVAÇÕES TÉCNICAS ADICIONAIS", section_style))
        story.append(Paragraph(obs, normal_style))
        story.append(Spacer(1, 20))

    # 6. Assinatura do Técnico
    sig_data = [
        ["", Paragraph(f"______________________________________<br/><b>Assinatura do Técnico:</b> {tecnico}", ParagraphStyle("Sig", parent=normal_style, alignment=1))]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    story.append(t_sig)

    # Construir PDF
    doc.build(story)
    return str(output_path)
