from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from diagram_studio import __version__, normalize_spec
from diagram_studio.cli import build_parser
from diagram_studio.exporters import export_mermaid, mermaid_markdown
from diagram_studio.renderer import render_diagram, render_to_files
from diagram_studio.styles import STYLES


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
    assert (ROOT / "references" / "DIAGRAM.md").exists()
    assert (ROOT / "references" / "QUALITY_GATES.md").exists()


def test_package_version_matches_release_surface() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert __version__ == "0.2.1"
    assert 'version = "0.2.1"' in pyproject
    assert build_parser().format_usage().startswith("usage:")
    assert "ships the runtime CLI only" in readme


def test_render_examples_fails_loudly_without_a_source_examples_dir(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing-examples"

    result = subprocess.run(
        [sys.executable, "-m", "diagram_studio.cli", "render-examples", "--examples-dir", str(missing_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "examples directory not found" in result.stderr


def test_runtime_only_wheel_excludes_skill_repo_materials(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"

    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    wheel_path = next(dist_dir.glob("diagram_studio-0.2.1-*.whl"))
    with zipfile.ZipFile(wheel_path) as wheel:
        names = wheel.namelist()
    normalized_names = [f"/{name.lstrip('/')}" for name in names]

    assert "diagram_studio/specs.py" in names
    assert not any(
        "/SKILL.md" in name
        or any(fragment in name for fragment in ("/agents/", "/assets/", "/examples/", "/references/"))
        for name in normalized_names
    )


def test_renderer_accepts_documented_alias_fields() -> None:
    spec = {
        "styleFamily": "editorial-technical",
        "titleBlock": {
            "title": "Alias Title",
            "subtitle": "Alias Subtitle",
        },
        "nodes": [],
    }

    normalized = normalize_spec(spec)
    svg = render_diagram(spec)

    assert normalized["style"] == "editorial-technical"
    assert normalized["title_block"]["title"] == "Alias Title"
    assert STYLES["editorial-technical"]["app_bg"] in svg
    assert "Alias Title" in svg


def test_render_to_files_accepts_documented_alias_fields(tmp_path: Path) -> None:
    spec_path = tmp_path / "alias-spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "styleFamily": "editorial-technical",
                "canvas": {"width": 640, "height": 480},
                "canvasRegion": {"x": 10, "y": 20, "w": 620, "h": 440},
                "titleBlock": {"title": "Alias File Title"},
                "bottomBanner": {"x": 24, "y": 420, "w": 592, "h": 36, "text": "Alias Banner"},
                "nodes": [],
            }
        ),
        encoding="utf-8",
    )

    result = render_to_files(spec_path, tmp_path / "out", html=True)
    svg = result["svg"].read_text(encoding="utf-8")
    html = result["html"].read_text(encoding="utf-8")

    assert 'x="10" y="20" width="620" height="440"' in svg
    assert "Alias File Title" in svg
    assert "Alias Banner" in svg
    assert f'background:{STYLES["editorial-technical"]["app_bg"]};' in html


def test_mermaid_export_accepts_documented_alias_fields() -> None:
    spec = {
        "titleBlock": {"title": "Alias Title"},
        "nodes": [{"id": "bridge", "label": "Bridge", "x": 0, "y": 0, "w": 180, "h": 80}],
        "edges": [],
    }

    markdown = mermaid_markdown(spec)

    assert markdown.startswith("# Alias Title")
    assert "Bridge" in markdown


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
