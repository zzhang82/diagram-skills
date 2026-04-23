from __future__ import annotations

import re
from pathlib import Path

import pytest

from diagram_studio.exporters import export_mermaid
from diagram_studio.renderer import render_diagram, render_to_files


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def test_skill_metadata_is_discoverable() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<body>.*?)\n---", skill, re.DOTALL)

    assert match is not None
    frontmatter = match.group("body")
    assert "name: diagram-studio" in frontmatter
    assert "description:" in frontmatter
    assert "$diagram-studio" in (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")


def test_render_all_examples_to_svg_and_html(tmp_path: Path) -> None:
    specs = sorted(EXAMPLES.glob("*.json"))

    assert specs
    for spec_path in specs:
        result = render_to_files(spec_path, tmp_path, html=True)
        svg = result["svg"].read_text(encoding="utf-8")
        html = result["html"].read_text(encoding="utf-8")

        assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert spec_path.stem in result["svg"].name
        assert "<html><body" in html


def test_mermaid_export_writes_source_and_markdown(tmp_path: Path) -> None:
    result = export_mermaid(EXAMPLES / "agent_memory_bridge.json", tmp_path)

    mermaid = result["mmd"].read_text(encoding="utf-8")
    markdown = result["markdown"].read_text(encoding="utf-8")

    assert mermaid.startswith("flowchart LR")
    assert "```mermaid" in markdown
    assert "Agent Memory Bridge" in markdown


def test_unknown_style_fails_fast() -> None:
    with pytest.raises(ValueError, match="Unknown style"):
        render_diagram({"style": "missing-style"})


def test_minimal_spec_has_no_editor_chrome_by_default() -> None:
    svg = render_diagram({"canvas": {"width": 640, "height": 480}, "nodes": []})

    assert "Diagram Studio" not in svg
    assert "Library" not in svg
    assert ">100%</text>" not in svg
    assert '<g stroke="' not in svg
