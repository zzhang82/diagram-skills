
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

Point = Tuple[float, float]


def _safe_id(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "node"


def _node_center(node: Dict[str, Any]) -> Point:
    return (node["x"] + node["w"] / 2, node["y"] + node["h"] / 2)


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _group_contains(group: Dict[str, Any], node: Dict[str, Any]) -> bool:
    nx, ny = _node_center(node)
    return group["x"] <= nx <= group["x"] + group["w"] and group["y"] <= ny <= group["y"] + group["h"]


def spec_to_mermaid(spec: Dict[str, Any]) -> str:
    nodes = spec.get("nodes", [])
    groups = spec.get("groups", [])
    edges = spec.get("edges", [])

    if not nodes:
        return "flowchart LR\n  empty[\"Empty diagram spec\"]"

    node_ids: Dict[str, str] = {}
    for idx, node in enumerate(nodes, start=1):
        nid = node.get("id") or f"node_{idx}"
        node_ids[nid] = _safe_id(nid)

    # assign nodes to first containing group
    group_members: Dict[str, List[Dict[str, Any]]] = {g.get("label", f"group_{i}"): [] for i, g in enumerate(groups, start=1)}
    ungrouped: List[Dict[str, Any]] = []
    for node in nodes:
        placed = False
        for group in groups:
            if _group_contains(group, node):
                group_members[group.get("label", "group")].append(node)
                placed = True
                break
        if not placed:
            ungrouped.append(node)

    lines: List[str] = ["flowchart LR"]

    # nodes inside subgraphs
    for i, group in enumerate(groups, start=1):
        label = group.get("label", f"Group {i}")
        gid = _safe_id(label)
        members = group_members.get(label, [])
        if not members:
            continue
        lines.append(f'  subgraph {gid}["{label}"]')
        for node in members:
            nid = node_ids[node.get("id") or ""]
            label_text = node.get("label", nid).replace("\n", "<br/>")
            lines.append(f'    {nid}["{label_text}"]')
        lines.append("  end")

    for node in ungrouped:
        nid = node_ids[node.get("id") or ""]
        label_text = node.get("label", nid).replace("\n", "<br/>")
        lines.append(f'  {nid}["{label_text}"]')

    # infer connections from point-based edges
    seen: set[tuple[str, str]] = set()
    centers = {node.get("id") or f"node_{i}": _node_center(node) for i, node in enumerate(nodes, start=1)}
    for edge in edges:
        pts = edge.get("points") or []
        if len(pts) < 2:
            continue
        start = tuple(pts[0])
        end = tuple(pts[-1])

        start_node = min(nodes, key=lambda n: _distance(start, centers[n.get("id") or ""]))
        end_node = min(nodes, key=lambda n: _distance(end, centers[n.get("id") or ""]))

        sid = node_ids[start_node.get("id") or ""]
        eid = node_ids[end_node.get("id") or ""]
        if sid == eid or (sid, eid) in seen:
            continue
        seen.add((sid, eid))
        label = edge.get("label")
        connector = f' -->|"{label}"| ' if label else " --> "
        lines.append(f"  {sid}{connector}{eid}")

    # simple class defs
    tone_styles = {
        "accent": ("fill:#f4f7ff,stroke:#3b82f6,color:#0f172a", []),
        "purple": ("fill:#f7f2ff,stroke:#7c3aed,color:#0f172a", []),
        "orange": ("fill:#fff6ed,stroke:#f97316,color:#0f172a", []),
        "success": ("fill:#f0fdf4,stroke:#16a34a,color:#0f172a", []),
        "neutral": ("fill:#f8fafc,stroke:#cbd5e1,color:#0f172a", []),
    }
    for node in nodes:
        tone = node.get("tone", "neutral")
        nid = node_ids[node.get("id") or ""]
        if tone in tone_styles:
            tone_styles[tone][1].append(nid)

    for tone, (style, ids) in tone_styles.items():
        if ids:
            lines.append(f"  classDef {tone} {style}")
            lines.append(f"  class {','.join(ids)} {tone}")

    return "\n".join(lines)


def mermaid_markdown(spec: Dict[str, Any]) -> str:
    mermaid = spec_to_mermaid(spec)
    title = spec.get("title_block", {}).get("title") or spec.get("title") or "Diagram"
    return f"# {title}\n\n```mermaid\n{mermaid}\n```\n"


def export_mermaid(spec_path: Path, outdir: Path) -> Dict[str, Path]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    outdir.mkdir(parents=True, exist_ok=True)
    stem = spec_path.stem
    mermaid = spec_to_mermaid(spec)
    md = mermaid_markdown(spec)

    mmd_path = outdir / f"{stem}.mmd"
    md_path = outdir / f"{stem}.mermaid.md"
    mmd_path.write_text(mermaid, encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    return {"mmd": mmd_path, "markdown": md_path}
