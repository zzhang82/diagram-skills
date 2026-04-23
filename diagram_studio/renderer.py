from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .icons import render_icon, svg_escape
from .styles import STYLES, TONE_KEYS


Point = Tuple[float, float]
PNG_EXPORT_ERROR = (
    "PNG export requires the optional cairosvg dependency and native Cairo libraries. "
    "Install the Python extra with `pip install -e .[png]`, then install Cairo for your OS."
)


def rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.3f})"


def tone_colors(style: Dict[str, str], tone: str | None) -> Tuple[str, str]:
    tone = tone or "neutral"
    primary_key, soft_key = TONE_KEYS.get(tone, TONE_KEYS["neutral"])
    return style[primary_key], style[soft_key]

def _line_count(text: str | None) -> int:
    return max(1, len((text or '').split("\n")))


def _render_multiline_text(x: float, y: float, text: str, font_family: str, font_size: int, fill: str, font_weight: str | int = 400, anchor: str = "start", line_height: float = 1.22) -> str:
    lines = (text or "").split("\n")
    start_y = y - ((len(lines) - 1) * font_size * line_height) / 2
    out = [f'<text x="{x}" y="{start_y}" text-anchor="{anchor}" font-family="{font_family}" font-size="{font_size}" fill="{fill}" font-weight="{font_weight}">']
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else font_size * line_height
        out.append(f'<tspan x="{x}" dy="{dy}">{svg_escape(line)}</tspan>')
    out.append('</text>')
    return ''.join(out)


def render_diagram(spec: Dict[str, Any], style_name: str | None = None) -> str:
    style_name = style_name or spec.get("style", "product-minimal")
    if style_name not in STYLES:
        raise ValueError(f"Unknown style: {style_name}")
    style = STYLES[style_name]
    width = spec.get("canvas", {}).get("width", 1440)
    height = spec.get("canvas", {}).get("height", 1080)
    ui = spec.get("ui", {})
    show_topbar = ui.get("show_topbar", False)
    show_sidebar = ui.get("show_sidebar", False)
    show_footer = ui.get("show_footer", False)

    parts: List[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    parts.append(_defs(style, style_name))
    parts.append(f'<rect width="{width}" height="{height}" fill="{style["app_bg"]}"/>')

    if show_topbar:
        parts.append(_render_topbar(spec, style))
    if show_sidebar:
        parts.append(_render_sidebar(spec, style))
    if show_footer:
        parts.append(_render_footer(spec, style))

    canvas_region = spec.get(
        "canvas_region",
        {
            "x": 120 if show_sidebar else 0,
            "y": 88 if show_topbar else 0,
            "w": width - (120 if show_sidebar else 0),
            "h": height - (88 if show_topbar else 0) - (76 if show_footer else 0),
        },
    )
    parts.append(f'<rect x="{canvas_region["x"]}" y="{canvas_region["y"]}" width="{canvas_region["w"]}" height="{canvas_region["h"]}" fill="{style["canvas_bg"]}"/>')
    if spec.get("canvas", {}).get("grid", False):
        parts.append(_render_grid(canvas_region, style))

    if title_block := spec.get("title_block"):
        parts.append(_render_title_block(title_block, style, style_name))

    for lane in spec.get("lanes", []):
        parts.append(_render_lane(lane, style, style_name))
    for group in spec.get("groups", []):
        parts.append(_render_group(group, style, style_name))
    for edge in spec.get("edges", []):
        parts.append(_render_edge(edge, style, style_name))
    for node in spec.get("nodes", []):
        parts.append(_render_node(node, style, style_name))
    for panel in spec.get("panels", []):
        parts.append(_render_panel(panel, style, style_name))
    if banner := spec.get("bottom_banner"):
        parts.append(_render_bottom_banner(banner, style, style_name))

    if ui.get("show_canvas_toolbar"):
        parts.append(_render_canvas_toolbar(spec, style))
    if ui.get("show_minimap", False):
        parts.append(_render_minimap(spec, style, canvas_region))
    parts.append('</svg>')
    return "".join(parts)



def _defs(style: Dict[str, str], style_name: str) -> str:
    return f'''
    <defs>
      <filter id="shadow-soft" x="-20%" y="-20%" width="140%" height="160%">
        <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="{rgba('#122033', 0.08)}"/>
      </filter>
      <filter id="shadow-depth" x="-20%" y="-20%" width="150%" height="180%">
        <feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="{rgba('#10213c', 0.08)}"/>
        <feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="{rgba('#ffffff', 0.70)}"/>
      </filter>
      <filter id="shadow-dark" x="-20%" y="-20%" width="140%" height="160%">
        <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="{rgba('#000000', 0.45)}"/>
      </filter>
      <filter id="shadow-none"><feDropShadow dx="0" dy="0" stdDeviation="0" flood-color="transparent"/></filter>
      <linearGradient id="neo-sheen" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="{rgba('#ffffff', 0.92)}"/>
        <stop offset="100%" stop-color="{rgba('#ffffff', 0.42)}"/>
      </linearGradient>
      <marker id="arrow-default" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="{style['text'] if style_name == 'editorial-technical' else style['muted']}"/>
      </marker>
      <marker id="arrow-accent" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="{style['accent']}"/>
      </marker>
      <marker id="arrow-danger" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="userSpaceOnUse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="{style['danger']}"/>
      </marker>
    </defs>
    '''


def _render_grid(region: Dict[str, float], style: Dict[str, str]) -> str:
    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
    step = 24
    lines = [f'<g stroke="{style["grid"]}" stroke-width="1">']
    for xi in range(int(x), int(x + w) + 1, step):
        lines.append(f'<line x1="{xi}" y1="{y}" x2="{xi}" y2="{y+h}" opacity="0.55"/>')
    for yi in range(int(y), int(y + h) + 1, step):
        lines.append(f'<line x1="{x}" y1="{yi}" x2="{x+w}" y2="{yi}" opacity="0.55"/>')
    lines.append('</g>')
    return ''.join(lines)


def _round_rect(x: float, y: float, w: float, h: float, r: float, fill: str, stroke: str, sw: float = 1.4, filter_id: str | None = None, extra: str = "") -> str:
    flt = f' filter="url(#{filter_id})"' if filter_id else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{flt} {extra}/>'


def _render_topbar(spec: Dict[str, Any], style: Dict[str, str]) -> str:
    width = spec.get("canvas", {}).get("width", 1440)
    title = svg_escape(spec.get("ui", {}).get("app_title", spec.get("title", "Diagram Studio")))
    subtitle = svg_escape(spec.get("ui", {}).get("app_subtitle", ""))
    style_selector = spec.get("ui", {}).get("style_selector")
    parts = [
        f'<rect x="0" y="0" width="{width}" height="88" fill="{style["topbar_bg"]}" stroke="{style["border"]}" stroke-width="1"/>',
        _round_rect(20, 20, 40, 40, 10, style["accent_soft"], style["accent"], 0),
        f'<text x="40" y="47" text-anchor="middle" font-family="{style["heading_font"]}" font-size="20" fill="{style["accent"]}" font-weight="700">⬢</text>',
        f'<text x="88" y="40" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="16" font-weight="700" fill="{style["text"]}">{title}</text>',
    ]
    if subtitle:
        parts.append(f'<text x="88" y="62" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="11" fill="{style["muted"]}">{subtitle}</text>')
    x = 1060
    if style_selector:
        parts.append(_round_rect(584, 24, 182, 38, 10, style["canvas_bg"], style["border"], 1.0))
        parts.append(f'<text x="600" y="48" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="14" fill="{style["muted"]}">Style</text>')
        parts.append(f'<text x="648" y="48" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="14" fill="{style["text"]}">{svg_escape(style_selector)}</text>')
    for cx, txt in ((1094, "⌕"), (1142, "?"), (1190, "◔")):
        parts.append(_round_rect(cx, 20, 34, 34, 12, style["canvas_bg"], style["border"], 1))
        parts.append(f'<text x="{cx+17}" y="43" text-anchor="middle" font-family="Inter, Segoe UI Symbol, Arial" font-size="15" fill="{style["muted"]}">{txt}</text>')
    parts.append(_round_rect(1238, 20, 40, 40, 20, rgba(style["text"], 0.9) if spec.get("style") == "operator-dark" else rgba(style["text"], 0.9), style["border"], 0))
    parts.append(f'<text x="1258" y="46" text-anchor="middle" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="14" fill="white">AK</text>')
    parts.append(_round_rect(1292, 20, 96, 40, 12, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="1340" y="45" text-anchor="middle" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="15" fill="{style["text"]}">Share</text>')
    parts.append(_round_rect(1406, 20, 120, 40, 12, style["accent"], style["accent"], 0))
    parts.append(f'<text x="1466" y="45" text-anchor="middle" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="15" fill="white">Export ▾</text>')
    parts.append(_round_rect(1080, 100, 48, 36, 10, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="1104" y="123" text-anchor="middle" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="14" fill="{style["text"]}">Fit</text>')
    parts.append(_round_rect(1138, 100, 164, 36, 10, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="1166" y="123" text-anchor="middle" font-size="20" font-family="Inter" fill="{style["muted"]}">−</text>')
    parts.append(f'<text x="1220" y="123" text-anchor="middle" font-size="15" font-family="Inter" fill="{style["text"]}">100%</text>')
    parts.append(f'<text x="1270" y="123" text-anchor="middle" font-size="20" font-family="Inter" fill="{style["muted"]}">+</text>')
    return ''.join(parts)


def _render_sidebar(spec: Dict[str, Any], style: Dict[str, str]) -> str:
    sidebar = spec.get("ui", {}).get("sidebar", {})
    width = sidebar.get("width", 236)
    height = spec.get("canvas", {}).get("height", 1080)
    top = 88
    items = sidebar.get("tabs", ["Library", "Layers", "Notes"])
    groups = sidebar.get("groups", [])
    components = sidebar.get("components", [])
    connectors = sidebar.get("connectors", [])
    parts = [f'<rect x="0" y="88" width="{width}" height="{height-top}" fill="{style["sidebar_bg"]}" stroke="{style["border"]}" stroke-width="1"/>']
    x = 20
    for i, label in enumerate(items):
        active = i == 0
        color = style["accent"] if active else style["muted"]
        parts.append(f'<text x="{x+12}" y="124" font-family="Inter" font-size="14" fill="{color}" font-weight="{700 if active else 500}">{svg_escape(label)}</text>')
        if active:
            parts.append(f'<line x1="{x}" y1="132" x2="{x+60}" y2="132" stroke="{style["accent"]}" stroke-width="2.5" stroke-linecap="round"/>')
        x += 74
    parts.append(_round_rect(20, 148, width-40, 40, 10, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="34" y="173" font-family="Inter" font-size="14" fill="{style["muted"]}">Search components</text>')
    cursor = 228
    for header, items2 in (("GROUPS", groups), ("COMPONENTS", components), ("CONNECTORS", connectors)):
        parts.append(f'<text x="24" y="{cursor}" font-family="Inter" font-size="12" fill="{style["muted"]}" font-weight="700">{header}</text>')
        cursor += 30
        for item in items2:
            parts.append(f'<text x="34" y="{cursor}" font-family="Inter" font-size="14" fill="{style["text"]}">{svg_escape(item)}</text>')
            cursor += 30
        cursor += 8
    return ''.join(parts)


def _render_footer(spec: Dict[str, Any], style: Dict[str, str]) -> str:
    width = spec.get("canvas", {}).get("width", 1440)
    height = spec.get("canvas", {}).get("height", 1080)
    footer = spec.get("ui", {}).get("footer", {})
    parts = [f'<rect x="0" y="{height-76}" width="{width}" height="76" fill="{style["footer_bg"]}" stroke="{style["border"]}" stroke-width="1"/>']
    left = footer.get("left", "All systems operational")
    parts.append(f'<circle cx="44" cy="{height-38}" r="6" fill="{style["success"]}"/>')
    parts.append(f'<text x="62" y="{height-32}" font-family="Inter" font-size="14" fill="{style["muted"]}">{svg_escape(left)}</text>')
    x = 370
    for item in footer.get("metrics", []):
        label, value, tone = item["label"], item["value"], item.get("tone", "muted")
        color = style.get(tone, style["text"])
        parts.append(f'<text x="{x}" y="{height-40}" font-family="Inter" font-size="13" fill="{style["muted"]}">{svg_escape(label)}</text>')
        parts.append(f'<text x="{x}" y="{height-16}" font-family="Inter" font-size="14" font-weight="700" fill="{color}">{svg_escape(value)}</text>')
        x += 122
    parts.append(f'<text x="{width-178}" y="{height-24}" font-family="Inter" font-size="14" fill="{style["muted"]}">Updated just now</text>')
    return ''.join(parts)


def _render_title_block(block: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    x, y = block["x"], block["y"]
    title = svg_escape(block["title"])
    subtitle = svg_escape(block.get("subtitle", ""))
    meta = block.get("meta", [])
    parts = []
    logo = block.get("logo")
    if logo:
        lx = logo.get("x", x - 64)
        ly = logo.get("y", y - 54)
        bg = logo.get("bg", style[logo.get("tone", "purple") + "_soft"] if logo.get("tone") in {"accent","success","warning","danger","purple","orange","teal"} else style["accent_soft"])
        fg = style.get(logo.get("tone", "purple"), style["accent"])
        parts.append(_round_rect(lx, ly, logo.get("w", 42), logo.get("h", 42), 12, bg, bg, 0))
        parts.append(f'<text x="{lx + logo.get("w",42)/2}" y="{ly + logo.get("h",42)/2 + 7}" text-anchor="middle" font-family="Inter" font-size="24" fill="{fg}" font-weight="800">{svg_escape(logo.get("mark", "M"))}</text>')
    parts.append(f'<text x="{x}" y="{y}" font-family="{style["heading_font"]}" font-size="{block.get("size", 56)}" font-weight="800" fill="{block.get("title_color", style["text"])}">{title}</text>')
    if subtitle:
        parts.append(f'<text x="{x}" y="{y+42}" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="18" fill="{block.get("subtitle_color", style["muted"])}">{subtitle}</text>')
    mx = x
    my = y + 84
    for pill in meta:
        fill = style.get(f"{pill.get('tone', 'accent')}_soft", style["accent_soft"])
        color = style.get(pill.get('tone', 'accent'), style["accent"])
        pill_text = svg_escape(pill["label"])
        w = 16 + len(pill_text) * 8.0
        parts.append(_round_rect(mx, my-18, w, 28, 14, fill, fill, 0))
        parts.append(f'<text x="{mx+w/2}" y="{my+1}" text-anchor="middle" font-family="Inter" font-size="14" fill="{color}" font-weight="600">{pill_text}</text>')
        mx += w + 14
    return ''.join(parts)


def _render_lane(lane: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    primary, soft = tone_colors(style, lane.get("tone", "neutral"))
    x, y, w, h = lane["x"], lane["y"], lane["w"], lane["h"]
    label_w = lane.get("label_w", 120)
    fill = rgba(soft.replace('#',''), 0) if False else rgba(soft, style["lane_alpha"]) if soft.startswith('#') else soft
    border = rgba(primary, 0.22) if primary.startswith('#') else primary
    parts = [_round_rect(x, y, w, h, lane.get("r", 18), fill, border, 1.2)]
    parts.append(f'<line x1="{x+label_w}" y1="{y}" x2="{x+label_w}" y2="{y+h}" stroke="{rgba(style["border"], 0.9)}" stroke-width="1"/>')
    parts.append(f'<text x="{x+24}" y="{y+50}" font-family="Inter" font-size="14" fill="{primary}" font-weight="700">{svg_escape(lane["label"])} </text>')
    return ''.join(parts)


def _render_group(group: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    primary, soft = tone_colors(style, group.get("tone", "accent"))
    x, y, w, h = group["x"], group["y"], group["w"], group["h"]
    alpha = group.get("alpha", style["group_alpha"])
    if style_name == "operator-dark":
        fill = rgba(soft, 0.7)
        stroke = rgba(primary, 0.75)
    else:
        fill = rgba(soft, alpha)
        stroke = rgba(primary, 0.45)
    filter_id = style["shadow"] if style_name in {"product-minimal", "neo-depth"} else None
    parts = [_round_rect(x, y, w, h, group.get("r", 22), fill, stroke, 1.4, filter_id if group.get("depth", style_name in {"product-minimal","neo-depth"}) else None)]
    if style_name == "neo-depth":
        parts.append(_round_rect(x+1, y+1, w-2, 14, group.get("r", 22), 'url(#neo-sheen)', 'none', 0))
    if section_num := group.get("section_num"):
        parts.append(_round_rect(x+18, y+18, 28, 28, 14, primary, primary, 0))
        parts.append(f'<text x="{x+32}" y="{y+38}" text-anchor="middle" font-family="Inter" font-size="15" fill="white" font-weight="700">{svg_escape(str(section_num))}</text>')
        label_x = x + 56
    else:
        label_x = x + 20
    parts.append(f'<text x="{label_x}" y="{y+39}" font-family="Inter" font-size="15" fill="{primary}" font-weight="800">{svg_escape(group["label"])}</text>')
    return ''.join(parts)


def _edge_path(points: Iterable[Point]) -> str:
    pts = list(points)
    if not pts:
        return ""
    out = [f'M {pts[0][0]} {pts[0][1]}']
    for x, y in pts[1:]:
        out.append(f'L {x} {y}')
    return ' '.join(out)


def _render_edge(edge: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    tone = edge.get("tone", "default")
    color = style["muted"]
    marker = "url(#arrow-default)"
    if tone == "accent":
        color, marker = style["accent"], "url(#arrow-accent)"
    elif tone == "danger":
        color, marker = style["danger"], "url(#arrow-danger)"
    elif tone == "success":
        color, marker = style["success"], "url(#arrow-accent)"
    elif tone == "warning":
        color, marker = style["warning"], "url(#arrow-accent)"
    width = edge.get("width", 2.2 if style_name == "editorial-technical" else 2.0)
    dash = edge.get("dash")
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    d = _edge_path(edge["points"])
    parts = []
    if style_name == "neo-depth" and edge.get("glow"):
        parts.append(f'<path d="{d}" fill="none" stroke="{rgba(color, 0.18)}" stroke-width="{width+6}" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" marker-end="{marker}"{dash_attr}/>' )
    if label := edge.get("label"):
        lx, ly = edge.get("label_pos", edge["points"][len(edge["points"]) // 2])
        fill = style["canvas_bg"] if style_name != "operator-dark" else style["node_bg"]
        parts.append(_round_rect(lx-26, ly-14, max(52, len(label)*9), 24, 10, fill, 'none', 0))
        parts.append(f'<text x="{lx}" y="{ly+4}" font-family="Inter" font-size="13" fill="{color}" font-weight="600">{svg_escape(label)}</text>')
    return ''.join(parts)


def _render_chip(x: float, y: float, label: str, tone: str, style: Dict[str, str]) -> str:
    primary, soft = tone_colors(style, tone)
    w = 14 + len(label) * 7.4
    return ''.join([
        _round_rect(x, y, w, 24, 12, soft, soft, 0),
        f'<text x="{x+w/2}" y="{y+16}" text-anchor="middle" font-family="Inter" font-size="12" fill="{primary}" font-weight="700">{svg_escape(label)}</text>',
    ])


def _render_node(node: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    tone = node.get("tone", "neutral")
    primary, soft = tone_colors(style, tone)
    filter_id = node.get("filter") or style["shadow"]
    parts: List[str] = []
    if node.get("shape", "rect") == "diamond":
        cx, cy = x + w/2, y + h/2
        pts = [(cx, y), (x+w, cy), (cx, y+h), (x, cy)]
        if style_name == "neo-depth":
            parts.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in pts)}" fill="{style["node_bg"]}" stroke="{primary}" stroke-width="1.4" filter="url(#{filter_id})"/>')
            parts.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in pts)}" fill="url(#neo-sheen)" stroke="none" opacity="0.55"/>')
        else:
            flt = ' filter="url(#shadow-soft)"' if style_name == 'product-minimal' else ''
            stroke = primary if style_name != 'editorial-technical' else style['border']
            parts.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in pts)}" fill="{style["node_bg"]}" stroke="{stroke}" stroke-width="1.4"{flt}/>')
        if node.get("icon"):
            parts.append(_round_rect(cx-16, y+18, 32, 32, 16, soft, 'none', 0))
            parts.append(render_icon(node["icon"], cx-8, y+26, 16, primary))
        parts.append(_render_multiline_text(cx, cy + (10 if node.get("icon") else 6), node["label"], 'Inter', node.get('label_size', 13), style['text'], 700, anchor='middle'))
    else:
        radius = node.get('r', 18)
        depth_default = style_name in {"product-minimal", "neo-depth", "operator-dark"}
        parts.append(_round_rect(x, y, w, h, radius, style['node_bg'], primary if node.get('stroke_tone') else style['border'], 1.3, filter_id if node.get('depth', depth_default) else None))
        if style_name == 'neo-depth':
            parts.append(_round_rect(x+1, y+1, w-2, 14, radius, 'url(#neo-sheen)', 'none', 0))
        icon_size = node.get('icon_box_size', 34 if h <= 62 else 40)
        icon_pad = node.get('icon_pad', 16 if h <= 62 else 18)
        if icon := node.get('icon'):
            parts.append(_round_rect(x+icon_pad, y+(h-icon_size)/2-8 if h<=62 else y+18, icon_size, icon_size, icon_size/2, soft, 'none', 0))
            parts.append(render_icon(icon, x+icon_pad+8, y+(h-icon_size)/2 if h<=62 else y+26, icon_size-16, primary))
        compact = h <= 62
        label_x = x + (w/2 if not node.get('icon') else icon_pad + icon_size + 14)
        anchor = 'middle' if not node.get('icon') else 'start'
        label_y = y + (h/2 + (2 if compact else -2))
        parts.append(_render_multiline_text(label_x, label_y, node['label'], 'Inter', node.get('label_size', 13 if compact else 16), style['text'], 700, anchor=anchor))
        if sub := node.get('subtext'):
            sub_y = y + (h/2 + 18 if compact else y + h - 18)
            if compact:
                parts.append(f'<text x="{label_x}" y="{sub_y}" text-anchor="{anchor}" font-family="Inter" font-size="11" fill="{style["muted"]}">{svg_escape(sub)}</text>')
            else:
                parts.append(f'<text x="{label_x}" y="{sub_y}" text-anchor="{anchor}" font-family="Inter" font-size="12" fill="{style["muted"]}">{svg_escape(sub)}</text>')
        if chip := node.get('chip'):
            chip_w = 14 + len(chip['label']) * 7.4
            parts.append(_render_chip(x + (w/2 - chip_w/2), y+h-34, chip['label'], chip.get('tone', tone), style))
    return ''.join(parts)


def _render_panel(panel: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    x, y, w, h = panel["x"], panel["y"], panel["w"], panel["h"]
    tone = panel.get("tone", "neutral")
    primary, soft = tone_colors(style, tone)
    fill = panel.get('fill') or (rgba(soft, panel.get('fill_alpha', 0.18)) if style_name != 'operator-dark' else style['node_bg'])
    parts = [_round_rect(x, y, w, h, panel.get("r", 20), fill if panel.get('use_fill', True) else style["node_bg"], style["border"], 1.2, style["shadow"] if style_name in {"product-minimal", "neo-depth"} else None)]
    title = panel.get('title')
    header_y = y + 38
    if title:
        if panel.get('icon'):
            parts.append(_round_rect(x+22, y+18, 30, 30, 15, rgba(primary, 0.12), 'none', 0))
            parts.append(render_icon(panel['icon'], x+29, y+25, 16, primary))
            title_x = x + 66
        else:
            title_x = x + 24
        parts.append(f'<text x="{title_x}" y="{header_y}" font-family="Inter" font-size="15" fill="{primary}" font-weight="800">{svg_escape(title)}</text>')
    cursor = y + (68 if title else 34)
    for row in panel.get("rows", []):
        icon = row.get("icon", "info")
        parts.append(render_icon(icon, x+22, cursor-14, 18, style["muted"]))
        parts.append(f'<text x="{x+52}" y="{cursor}" font-family="Inter" font-size="13" fill="{style["muted"]}">{svg_escape(row["label"])} </text>')
        parts.append(f'<text x="{x+w-24}" y="{cursor}" text-anchor="end" font-family="Inter" font-size="13" fill="{style["text"]}">{svg_escape(row["value"])} </text>')
        cursor += 30
    bullets = panel.get('bullets', [])
    if bullets:
        yy = cursor
        for item in bullets:
            parts.append(f'<circle cx="{x+30}" cy="{yy-5}" r="4" fill="{primary}"/>')
            parts.append(f'<text x="{x+46}" y="{yy}" font-family="Inter" font-size="13" fill="{style["text"]}">{svg_escape(item)}</text>')
            yy += 28
        cursor = yy
    if body := panel.get("body"):
        lines = body.split("\n")
        yy = cursor if (panel.get('rows') or bullets) else y + (68 if title else 34)
        for line in lines:
            if not line:
                yy += 10
                continue
            parts.append(f'<text x="{x+24}" y="{yy}" font-family="Inter" font-size="13" fill="{style["muted"]}">{svg_escape(line)}</text>')
            yy += 22
    if items := panel.get("legend"):
        yy = y + 42
        for item in items:
            parts.append(f'<circle cx="{x+26}" cy="{yy-4}" r="5" fill="{style.get(item.get("tone", "accent"), style["accent"])}"/>')
            parts.append(f'<text x="{x+42}" y="{yy}" font-family="Inter" font-size="13" fill="{style["text"]}">{svg_escape(item["label"])} </text>')
            parts.append(f'<text x="{x+w-24}" y="{yy}" text-anchor="end" font-family="Inter" font-size="13" fill="{style["muted"]}">{svg_escape(item["value"])} </text>')
            yy += 28
    return ''.join(parts)


def _render_bottom_banner(banner: Dict[str, Any], style: Dict[str, str], style_name: str) -> str:
    x, y, w, h = banner['x'], banner['y'], banner['w'], banner['h']
    tone = banner.get('tone', 'accent')
    primary, soft = tone_colors(style, tone)
    parts = [_round_rect(x, y, w, h, banner.get('r', 16), rgba(soft, banner.get('fill_alpha', 0.22)), style['border'], 1.0, style['shadow'] if style_name in {'product-minimal','neo-depth'} else None)]
    if banner.get('icon'):
        parts.append(_round_rect(x+18, y+10, 28, 28, 14, rgba(primary, 0.12), 'none', 0))
        parts.append(render_icon(banner['icon'], x+24, y+16, 16, primary))
        text_x = x + 62
    else:
        text_x = x + 24
    parts.append(f'<text x="{text_x}" y="{y + h/2 + 5}" font-family="Inter" font-size="15" fill="{primary}" font-weight="700">{svg_escape(banner["text"])}</text>')
    return ''.join(parts)


def _render_canvas_toolbar(spec: Dict[str, Any], style: Dict[str, str]) -> str:
    toolbar = spec.get("ui", {}).get("canvas_toolbar", {"x": 1180, "y": 138, "items": ["↖", "—", "T", "▢"]})
    x, y = toolbar["x"], toolbar["y"]
    parts = [_round_rect(x, y, 220, 44, 14, style["node_bg"], style["border"], 1, style["shadow"] if spec.get("style") != "editorial-technical" else None)]
    for i, item in enumerate(toolbar.get("items", [])):
        parts.append(_round_rect(x+10 + i*50, y+6, 34, 32, 10, style["canvas_bg"], style["border"], 0))
        parts.append(f'<text x="{x+27 + i*50}" y="{y+27}" text-anchor="middle" font-family="Inter" font-size="16" fill="{style["muted"]}">{svg_escape(item)}</text>')
    return ''.join(parts)


def _render_minimap(spec: Dict[str, Any], style: Dict[str, str], canvas_region: Dict[str, float]) -> str:
    width = spec.get("canvas", {}).get("width", 1440)
    height = spec.get("canvas", {}).get("height", 1080)
    x = width - 186
    y = height - (212 if spec.get("ui", {}).get("show_footer", False) else 160)
    panel_w, panel_h = 150, 126
    parts = [_round_rect(x, y, panel_w, panel_h, 16, style["node_bg"], style["border"], 1, style["shadow"] if spec.get("style") in {"product-minimal", "neo-depth"} else None)]
    mini_x, mini_y, mini_w, mini_h = x+16, y+14, 118, 76
    parts.append(_round_rect(mini_x, mini_y, mini_w, mini_h, 10, style["canvas_bg"], style["border"], 1))
    nodes = spec.get("nodes", [])
    if nodes:
        minx = min(n["x"] for n in nodes)
        miny = min(n["y"] for n in nodes)
        maxx = max(n["x"] + n["w"] for n in nodes)
        maxy = max(n["y"] + n["h"] for n in nodes)
        dx = max(maxx - minx, 1)
        dy = max(maxy - miny, 1)
        scale = min(mini_w / dx, mini_h / dy)
        for n in nodes:
            nx = mini_x + (n["x"] - minx) * scale
            ny = mini_y + (n["y"] - miny) * scale
            nw = max(8, n["w"] * scale)
            nh = max(6, n["h"] * scale)
            parts.append(_round_rect(nx, ny, nw, nh, 4, rgba(style["accent"], 0.12), rgba(style["accent"], 0.35), 0.7))
        parts.append(_round_rect(mini_x+3, mini_y+3, mini_w-6, mini_h-6, 8, 'none', style["accent"], 2))
    parts.append(_round_rect(x+18, y+96, 32, 18, 9, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="{x+34}" y="{y+109}" text-anchor="middle" font-family="Inter" font-size="14" fill="{style["muted"]}">−</text>')
    parts.append(f'<text x="{x+75}" y="{y+109}" text-anchor="middle" font-family="Inter" font-size="12" fill="{style["text"]}">100%</text>')
    parts.append(_round_rect(x+101, y+96, 32, 18, 9, style["canvas_bg"], style["border"], 1))
    parts.append(f'<text x="{x+117}" y="{y+109}" text-anchor="middle" font-family="Inter" font-size="14" fill="{style["muted"]}">+</text>')
    return ''.join(parts)


def render_to_files(spec_path: Path, outdir: Path, style_name: str | None = None, png: bool = False, html: bool = True) -> Dict[str, Path]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    svg = render_diagram(spec, style_name)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = spec_path.stem + (f"-{style_name}" if style_name else "")
    svg_path = outdir / f"{stem}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    result = {"svg": svg_path}
    if html:
        html_path = outdir / f"{stem}.html"
        background = STYLES[style_name or spec.get("style", "product-minimal")]["app_bg"]
        html_doc = (
            '<html><body style="margin:0;'
            f"background:{background};"
            'display:flex;align-items:center;justify-content:center;'
            f'min-height:100vh;">{svg}</body></html>'
        )
        html_path.write_text(html_doc, encoding="utf-8")
        result["html"] = html_path
    if png:
        try:
            import cairosvg
        except (ImportError, OSError) as exc:
            raise RuntimeError(PNG_EXPORT_ERROR) from exc

        png_path = outdir / f"{stem}.png"
        try:
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path), scale=1.0)
        except OSError as exc:
            raise RuntimeError(PNG_EXPORT_ERROR) from exc
        result["png"] = png_path
    return result
