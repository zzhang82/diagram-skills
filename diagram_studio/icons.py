from math import cos, sin, pi


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _line(x1, y1, x2, y2, stroke, width=1.8, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" {extra}/>'


def _rect(x, y, w, h, stroke, width=1.8, fill="none", rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def _circle(cx, cy, r, stroke, width=1.8, fill="none"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def render_icon(name: str, x: float, y: float, size: float, stroke: str) -> str:
    cx = x + size / 2
    cy = y + size / 2
    s = size
    parts = ['<g fill="none" stroke-linecap="round" stroke-linejoin="round">']
    name = (name or "dot").lower()

    if name == "user":
        parts.append(_circle(cx, y + s * 0.35, s * 0.16, stroke))
        parts.append(f'<path d="M {x + s*0.2} {y+s*0.78} C {x+s*0.28} {y+s*0.58}, {x+s*0.72} {y+s*0.58}, {x+s*0.8} {y+s*0.78}" stroke="{stroke}" stroke-width="1.8"/>')
    elif name in {"web", "browser", "monitor"}:
        parts.append(_rect(x + s * 0.16, y + s * 0.18, s * 0.68, s * 0.48, stroke, rx=5))
        parts.append(_line(cx, y + s * 0.67, cx, y + s * 0.82, stroke))
        parts.append(_line(x + s * 0.33, y + s * 0.82, x + s * 0.67, y + s * 0.82, stroke))
    elif name in {"phone", "mobile"}:
        parts.append(_rect(x + s * 0.28, y + s * 0.12, s * 0.44, s * 0.76, stroke, rx=6))
        parts.append(_circle(cx, y + s * 0.78, s * 0.03, stroke, fill=stroke))
    elif name in {"gateway", "hex", "service"}:
        pts = []
        for i in range(6):
            ang = -pi / 2 + i * pi / 3
            pts.append(f"{cx + cos(ang)*s*0.3},{cy + sin(ang)*s*0.3}")
        parts.append(f'<polygon points="{" ".join(pts)}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
        parts.append(_line(cx, cy - s*0.17, cx, cy + s*0.17, stroke))
    elif name in {"database", "db", "postgres"}:
        parts.append(f'<ellipse cx="{cx}" cy="{y+s*0.22}" rx="{s*0.24}" ry="{s*0.11}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
        parts.append(_line(x+s*0.26, y+s*0.22, x+s*0.26, y+s*0.72, stroke))
        parts.append(_line(x+s*0.74, y+s*0.22, x+s*0.74, y+s*0.72, stroke))
        parts.append(f'<path d="M {x+s*0.26} {y+s*0.72} C {x+s*0.32} {y+s*0.83}, {x+s*0.68} {y+s*0.83}, {x+s*0.74} {y+s*0.72}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
        parts.append(f'<path d="M {x+s*0.26} {y+s*0.47} C {x+s*0.32} {y+s*0.58}, {x+s*0.68} {y+s*0.58}, {x+s*0.74} {y+s*0.47}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
    elif name in {"queue", "async", "lines"}:
        for i in range(4):
            x0 = x + s*(0.22 + 0.12*i)
            parts.append(_line(x0, y+s*0.24, x0, y+s*0.76, stroke))
    elif name in {"email", "mail"}:
        parts.append(_rect(x + s * 0.18, y + s * 0.24, s * 0.64, s * 0.46, stroke, rx=4))
        parts.append(_line(x + s * 0.19, y + s * 0.26, cx, y + s * 0.52, stroke))
        parts.append(_line(cx, y + s * 0.52, x + s * 0.81, y + s * 0.26, stroke))
    elif name in {"worker", "gear"}:
        parts.append(_circle(cx, cy, s*0.18, stroke))
        parts.append(_circle(cx, cy, s*0.07, stroke))
        for i in range(8):
            ang = i*pi/4
            r1, r2 = s*0.24, s*0.33
            parts.append(_line(cx + cos(ang)*r1, cy + sin(ang)*r1, cx + cos(ang)*r2, cy + sin(ang)*r2, stroke, width=1.5))
    elif name in {"lock", "auth"}:
        parts.append(_rect(x + s*0.27, y+s*0.42, s*0.46, s*0.34, stroke, rx=4))
        parts.append(f'<path d="M {x+s*0.36} {y+s*0.42} V {y+s*0.31} a {s*0.14} {s*0.14} 0 0 1 {s*0.28} 0 v {s*0.11}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
    elif name in {"cube", "box"}:
        pts1 = [(cx, y+s*0.16),(x+s*0.72, y+s*0.3),(cx, y+s*0.44),(x+s*0.28,y+s*0.3)]
        pts2 = [(cx, y+s*0.44),(cx,y+s*0.74),(x+s*0.72,y+s*0.6),(x+s*0.72,y+s*0.3)]
        pts3 = [(cx, y+s*0.44),(cx,y+s*0.74),(x+s*0.28,y+s*0.6),(x+s*0.28,y+s*0.3)]
        for pts in (pts1, pts2, pts3):
            parts.append(f'<polyline points="{" ".join(f"{px},{py}" for px,py in pts)}" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
    elif name in {"note", "document", "postmortem"}:
        parts.append(_rect(x+s*0.23, y+s*0.15, s*0.5, s*0.7, stroke, rx=4))
        parts.append(_line(x+s*0.34, y+s*0.38, x+s*0.64, y+s*0.38, stroke))
        parts.append(_line(x+s*0.34, y+s*0.54, x+s*0.64, y+s*0.54, stroke))
    elif name in {"globe", "external", "stripe"}:
        parts.append(_circle(cx, cy, s*0.28, stroke))
        parts.append(_line(cx - s*0.28, cy, cx + s*0.28, cy, stroke))
        parts.append(_line(cx, cy - s*0.28, cx, cy + s*0.28, stroke))
        parts.append(f'<path d="M {cx-s*0.18} {cy-s*0.24} C {cx-s*0.03} {cy-s*0.08}, {cx-s*0.03} {cy+s*0.08}, {cx-s*0.18} {cy+s*0.24}" stroke="{stroke}" stroke-width="1.5" fill="none"/>')
        parts.append(f'<path d="M {cx+s*0.18} {cy-s*0.24} C {cx+s*0.03} {cy-s*0.08}, {cx+s*0.03} {cy+s*0.08}, {cx+s*0.18} {cy+s*0.24}" stroke="{stroke}" stroke-width="1.5" fill="none"/>')
    elif name in {"storage", "bucket", "object-storage"}:
        parts.append(f'<path d="M {x+s*0.28} {y+s*0.26} L {x+s*0.72} {y+s*0.26} L {x+s*0.64} {y+s*0.72} L {x+s*0.36} {y+s*0.72} Z" stroke="{stroke}" stroke-width="1.8" fill="none"/>')
    elif name in {"cache", "redis"}:
        for dy in (0.28, 0.48, 0.68):
            pts = [(cx, y+s*(dy-0.11)), (x+s*0.72, y+s*dy), (cx, y+s*(dy+0.11)), (x+s*0.28, y+s*dy)]
            parts.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in pts)}" stroke="{stroke}" stroke-width="1.6" fill="none"/>')
    elif name in {"play", "publish"}:
        parts.append(_circle(cx, cy, s*0.3, stroke))
        parts.append(f'<polygon points="{x+s*0.45},{y+s*0.38} {x+s*0.66},{cy} {x+s*0.45},{y+s*0.62}" fill="{stroke}" stroke="none"/>')
    elif name in {"info", "summary"}:
        parts.append(_circle(cx, cy, s*0.28, stroke))
        parts.append(_line(cx, y+s*0.42, cx, y+s*0.64, stroke))
        parts.append(_circle(cx, y+s*0.31, s*0.02, stroke, fill=stroke))
    else:
        parts.append(_circle(cx, cy, s*0.18, stroke, fill=stroke))

    parts.append("</g>")
    return "".join(parts)
