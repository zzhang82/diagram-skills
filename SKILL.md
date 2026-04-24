---
name: diagram-studio
description: Create polished software and system diagrams with presentation, editable, and portable outputs. Use when Codex needs to produce or refine architecture diagrams, workflows, flow charts, process charts, or memory and coordination diagrams.
---

# Diagram Studio Skill

## Purpose

Generate high-quality software diagrams with:
- simplification
- clear hierarchy
- restrained styling
- export flexibility

Keep internal implementation details secondary to user-facing output quality.

## Core contract

When using this skill:
1. understand the user's diagram intent
2. choose the best output mode
3. produce the clearest useful diagram
4. apply quality checks before export

Read `references/DIAGRAM.md` when changing design rules. Read `references/ROUTING_FIRST.md` only when changing backend-selection logic. Read `references/ROUTE_COMPARISON.md` when comparing image-model, structured renderer, and Mermaid outputs. Read `references/QUALITY_GATES.md` when changing validation heuristics.

## Primary diagram types

- flow charts
- architecture / component diagrams
- process charts
- system workflow diagrams
- memory / coordination diagrams

## Modes

### Presentation mode
Default.
Use when the user wants the result to look great.

Traits:
- title + subtitle
- optional explainer panel
- no fake editor chrome
- calmer palette
- presentation-led composition

Routing priority:
1. image model
2. React / SVG / HTML renderer
3. Mermaid / DSL fallback

### Editable mode
Use when the artifact should stay structured.

Traits:
- deterministic output
- easier iteration
- inspectable files

Routing priority:
1. React / SVG / HTML renderer
2. Mermaid / DSL

### Portable mode
Use when the user wants compatibility.

Traits:
- Mermaid / DSL source
- easy copy/paste into other tools
- lower visual ceiling accepted

Routing priority:
1. Mermaid / DSL
2. lightweight structured export

### Concept UI mode
Use only for design/product mockups.

Traits:
- optional editor chrome
- product screenshot style
- not default for real deliverables

## Presentation rules

- remove editor chrome unless explicitly requested
- prefer cleaner composition over maximum completeness
- reduce visible detail when the page feels crowded
- use one primary accent with restrained semantic colors
- keep explainer bullets compact
- preserve whitespace between major zones
- node sizing must fit text predictably

## Scope rules

### In scope
- 2D-first rendering
- soft depth polish
- restrained glass treatment
- subtle highlights
- compact explainer sections
- title/subtitle hierarchy
- route selection rules

### Out of scope
- full WebGL / true 3D diagrams
- flashy gradient overload
- toy-like extrusions
- fake editor chrome by default

## Current renderer input shape

The current renderer and Mermaid exporter consume concrete render fields like the following:

```json
{
  "style": "editorial-technical",
  "canvas": {
    "width": 1600,
    "height": 1100,
    "grid": false
  },
  "title_block": {
    "title": "Agent Memory Bridge",
    "subtitle": "Two-channel MCP memory for coding agents"
  },
  "ui": {
    "show_topbar": false,
    "show_sidebar": false,
    "show_minimap": false
  },
  "groups": [],
  "nodes": [],
  "edges": [],
  "panels": []
}
```

The runtime also accepts `styleFamily` and `titleBlock` as compatibility aliases when importing higher-level planning specs.

## Quality checks

Must check:
- text overflow
- too many major zones
- too much side-panel weight
- weak hierarchy
- overuse of color
- connector dominance
- crowded cards

## Backend guidance

### Image model
Best for:
- README hero graphics
- editorial architecture diagrams
- presentation-first charts

### React / SVG / HTML
Best for:
- deterministic exports
- editable artifacts
- repeatable structured rendering

### Mermaid / DSL
Best for:
- compatibility
- portability
- lightweight source handoff

## Success criterion

Before delivering, ensure the result:
- chooses the right abstraction level
- chooses the right backend
- stays visually calm
- avoids crowding
- produces an output appropriate for the requested mode
