from __future__ import annotations

import argparse
from pathlib import Path

from .exporters import export_mermaid
from .renderer import render_to_files
from .styles import STYLES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render polished software diagrams from JSON specs.")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="Render one spec to SVG/HTML/PNG")
    render.add_argument("spec", type=Path)
    render.add_argument("--outdir", type=Path, default=Path("generated"))
    render.add_argument("--style", choices=sorted(STYLES.keys()))
    render.add_argument("--png", action="store_true", help="Also export PNG with CairoSVG")
    render.add_argument("--no-html", action="store_true")

    batch = sub.add_parser("render-examples", help="Render all bundled examples")
    batch.add_argument("--examples-dir", type=Path, default=Path("examples"))
    batch.add_argument("--outdir", type=Path, default=Path("generated"))
    batch.add_argument("--png", action="store_true")

    mermaid = sub.add_parser("export-mermaid", help="Export one spec to Mermaid fallback files")
    mermaid.add_argument("spec", type=Path)
    mermaid.add_argument("--outdir", type=Path, default=Path("generated"))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "render":
        result = render_to_files(args.spec, args.outdir, style_name=args.style, png=args.png, html=not args.no_html)
        for key, path in result.items():
            print(f"{key}: {path}")
    elif args.command == "render-examples":
        for spec in sorted(args.examples_dir.glob("*.json")):
            result = render_to_files(spec, args.outdir, png=args.png, html=True)
            print(f"rendered {spec.name}")
            for key, path in result.items():
                print(f"  {key}: {path}")
    elif args.command == "export-mermaid":
        result = export_mermaid(args.spec, args.outdir)
        for key, path in result.items():
            print(f"{key}: {path}")


if __name__ == "__main__":
    main()
