"""
Utilitário de carregamento e renderização dos ícones vetoriais oficiais do Lucide Icons.
Ajustado para espessura fina, elegante e ultra-nítida.
"""
import io
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
import math
import tkinter as tk
from PIL import Image, ImageDraw
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ICONS_DIR = BASE_DIR / "app" / "assets" / "icons"

ICON_SVG_MAP = {
    "truck": "truck.svg",
    "file_text": "file-text.svg",
    "users": "users.svg",
    "gear": "settings.svg",
    "settings": "settings.svg",
    "logout": "log-out.svg",
    "landmark": "landmark.svg",
    "arrow_left": "arrow-left.svg",
    "calendar": "calendar.svg",
    "car": "car.svg",
    "tag": "tag.svg",
    "user": "user.svg",
    "eye": "eye.svg",
    "pencil": "pencil.svg",
    "edit": "pencil.svg",
    "trash": "trash-2.svg",
    "chevron_left": "chevron-left.svg",
    "chevron_right": "chevron-right.svg",
    "plus": "plus.svg",
    "clipboard_list": "clipboard-list.svg",
    "wrench": "wrench.svg",
    "map_pin": "map-pin.svg",
    "x": "x.svg",
    "search": "search.svg",
}

def pil_to_photoimage(img: Image.Image) -> tk.PhotoImage:
    """Converte uma imagem PIL para tk.PhotoImage usando buffer PNG em memória."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return tk.PhotoImage(data=buf.getvalue())

def ensure_svg_icon(icon_key: str) -> str:
    """Garante que o arquivo SVG oficial do Lucide existe no diretório de assets."""
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    svg_name = ICON_SVG_MAP.get(icon_key, f"{icon_key}.svg")
    svg_path = ICONS_DIR / svg_name

    if not svg_path.exists():
        url = f"https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{svg_name}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                content = resp.read()
                with open(svg_path, "wb") as f:
                    f.write(content)
        except Exception as e:
            print(f"Erro ao baixar ícone {svg_name}:", e)

    if svg_path.exists():
        with open(svg_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def parse_svg_path(d_str):
    """Parser para os caminhos de vetores (path d) do SVG."""
    tokens = re.findall(r"([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)", d_str)
    commands = []
    current_cmd = None
    nums = []

    for cmd, num in tokens:
        if cmd:
            if current_cmd:
                commands.append((current_cmd, nums))
            current_cmd = cmd
            nums = []
        elif num:
            nums.append(float(num))
    if current_cmd:
        commands.append((current_cmd, nums))

    subpaths = []
    curr_pts = []
    cx, cy = 0.0, 0.0
    start_x, start_y = 0.0, 0.0

    for cmd, args in commands:
        cmd_upper = cmd.upper()
        is_rel = cmd.islower()

        if cmd_upper == "M":
            for i in range(0, len(args), 2):
                x = args[i] + (cx if is_rel else 0)
                y = args[i+1] + (cy if is_rel else 0)
                if i == 0:
                    if curr_pts:
                        subpaths.append(curr_pts)
                    curr_pts = [(x, y)]
                    start_x, start_y = x, y
                else:
                    curr_pts.append((x, y))
                cx, cy = x, y

        elif cmd_upper == "L":
            for i in range(0, len(args), 2):
                x = args[i] + (cx if is_rel else 0)
                y = args[i+1] + (cy if is_rel else 0)
                curr_pts.append((x, y))
                cx, cy = x, y

        elif cmd_upper == "H":
            for val in args:
                x = val + (cx if is_rel else 0)
                curr_pts.append((x, cy))
                cx = x

        elif cmd_upper == "V":
            for val in args:
                y = val + (cy if is_rel else 0)
                curr_pts.append((cx, y))
                cy = y

        elif cmd_upper == "C":
            for i in range(0, len(args) - 5, 6):
                x1 = args[i] + (cx if is_rel else 0)
                y1 = args[i+1] + (cy if is_rel else 0)
                x2 = args[i+2] + (cx if is_rel else 0)
                y2 = args[i+3] + (cy if is_rel else 0)
                x3 = args[i+4] + (cx if is_rel else 0)
                y3 = args[i+5] + (cy if is_rel else 0)

                steps = 14
                for s in range(1, steps + 1):
                    t = s / steps
                    t_inv = 1 - t
                    px = (t_inv**3 * cx) + (3 * t_inv**2 * t * x1) + (3 * t_inv * t**2 * x2) + (t**3 * x3)
                    py = (t_inv**3 * cy) + (3 * t_inv**2 * t * y1) + (3 * t_inv * t**2 * y2) + (t**3 * y3)
                    curr_pts.append((px, py))
                cx, cy = x3, y3

        elif cmd_upper == "A":
            for i in range(0, len(args) - 6, 7):
                x = args[i+5] + (cx if is_rel else 0)
                y = args[i+6] + (cy if is_rel else 0)
                steps = 10
                for s in range(1, steps + 1):
                    t = s / steps
                    px = cx + (x - cx) * t
                    py = cy + (y - cy) * t
                    curr_pts.append((px, py))
                cx, cy = x, y

        elif cmd_upper == "Z":
            if curr_pts:
                curr_pts.append((start_x, start_y))
            cx, cy = start_x, start_y

    if curr_pts:
        subpaths.append(curr_pts)

    return subpaths

def draw_classic_gear(size: int, color: str = "#FFFFFF", stroke_width: float = 2.0) -> Image.Image:
    """Desenha o ícone mecânico clássico de engrenagem de 8 dentes proeminentes."""
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if color.startswith("#"):
        hex_val = color.lstrip("#")
        r, g, b = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
        rgba = (r, g, b, 255)
    else:
        rgba = (255, 255, 255, 255)

    pad = 5 * scale
    cx, cy = canvas_size / 2, canvas_size / 2
    r_out = canvas_size / 2 - pad
    r_in = r_out * 0.65
    r_hole = r_out * 0.3

    w = max(2, int(stroke_width * scale * 1.2))

    num_teeth = 8
    for i in range(num_teeth):
        angle = i * (2 * math.pi / num_teeth)
        dx = math.cos(angle) * r_out
        dy = math.sin(angle) * r_out
        draw.line([(cx, cy), (cx + dx, cy + dy)], fill=rgba, width=int(w * 2.0))

    draw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], outline=rgba, width=w)
    draw.ellipse([cx - r_hole, cy - r_hole, cx + r_hole, cy + r_hole], outline=rgba, width=w)

    return img.resize((size, size), Image.Resampling.LANCZOS)

def render_lucide_svg(svg_string: str, size: int = 48, color: str = "#FFFFFF", stroke_width: float = 1.6) -> Image.Image:
    """Renderiza a estrutura SVG oficial do Lucide em PIL Image."""
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if color.startswith("#"):
        hex_val = color.lstrip("#")
        r, g, b = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
        rgba = (r, g, b, 255)
    else:
        rgba = (255, 255, 255, 255)

    try:
        root = ET.fromstring(svg_string)
    except Exception as e:
        print("Erro ao parsear SVG:", e)
        return img.resize((size, size))

    s_factor = canvas_size / 24.0
    w = max(1, int(stroke_width * s_factor))

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]

        if tag == "path":
            d = elem.attrib.get("d", "")
            subpaths = parse_svg_path(d)
            for pts in subpaths:
                scaled_pts = [(x * s_factor, y * s_factor) for x, y in pts]
                if len(scaled_pts) > 1:
                    draw.line(scaled_pts, fill=rgba, width=w, joint="curve")

        elif tag == "circle":
            cx = float(elem.attrib.get("cx", 0)) * s_factor
            cy = float(elem.attrib.get("cy", 0)) * s_factor
            r = float(elem.attrib.get("r", 0)) * s_factor
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba, width=w)

        elif tag == "rect":
            x = float(elem.attrib.get("x", 0)) * s_factor
            y = float(elem.attrib.get("y", 0)) * s_factor
            rw = float(elem.attrib.get("width", 0)) * s_factor
            rh = float(elem.attrib.get("height", 0)) * s_factor
            rx = float(elem.attrib.get("rx", 0)) * s_factor
            if rx > 0:
                draw.rounded_rectangle([x, y, x + rw, y + rh], radius=rx, outline=rgba, width=w)
            else:
                draw.rectangle([x, y, x + rw, y + rh], outline=rgba, width=w)

        elif tag == "line":
            x1 = float(elem.attrib.get("x1", 0)) * s_factor
            y1 = float(elem.attrib.get("y1", 0)) * s_factor
            x2 = float(elem.attrib.get("x2", 0)) * s_factor
            y2 = float(elem.attrib.get("y2", 0)) * s_factor
            draw.line([(x1, y1), (x2, y2)], fill=rgba, width=w)

        elif tag == "polyline" or tag == "polygon":
            pts_str = elem.attrib.get("points", "")
            raw_nums = [float(n) for n in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", pts_str)]
            pts = [(raw_nums[i] * s_factor, raw_nums[i+1] * s_factor) for i in range(0, len(raw_nums)-1, 2)]
            if len(pts) > 1:
                if tag == "polygon":
                    draw.polygon(pts, outline=rgba, width=w)
                else:
                    draw.line(pts, fill=rgba, width=w)

    return img.resize((size, size), Image.Resampling.LANCZOS)

def create_icon_image(icon_name: str, size: int = 48, color: str = "#FFFFFF", stroke_width: float = 1.6) -> tk.PhotoImage:
    """
    Retorna o tk.PhotoImage do ícone solicitado.
    """
    if icon_name in ("gear", "settings_classic"):
        pil_img = draw_classic_gear(size=size, color=color, stroke_width=stroke_width)
        return pil_to_photoimage(pil_img)

    svg_string = ensure_svg_icon(icon_name)
    if svg_string:
        pil_img = render_lucide_svg(svg_string, size=size, color=color, stroke_width=stroke_width)
        return pil_to_photoimage(pil_img)

    fallback_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return pil_to_photoimage(fallback_img)
