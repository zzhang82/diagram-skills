from __future__ import annotations

from typing import Any, Dict


SPEC_ALIASES = {
    "styleFamily": "style",
    "titleBlock": "title_block",
    "canvasRegion": "canvas_region",
    "bottomBanner": "bottom_banner",
}


def normalize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Accept a small alias set so published examples and renderer inputs stay compatible."""
    normalized = dict(spec)
    for source_key, target_key in SPEC_ALIASES.items():
        if target_key not in normalized and source_key in normalized:
            normalized[target_key] = normalized[source_key]
    return normalized
