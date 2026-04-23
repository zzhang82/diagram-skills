# Routing-First Architecture

## Why routing first

The image-model reference concepts repeatedly beat the structured renderer on:
- composition
- whitespace
- typography feel
- explainer integration
- overall polish

That means the skill should not force every request through one renderer.

## Decision

Treat the skill as:

```text
planner + style rules + router + quality checks
```

not:

```text
one renderer to rule them all
```

## Canonical flow

```text
user request
-> parse intent
-> build DiagramSpec
-> choose mode
-> choose backend
-> render
-> quality check
-> export
```

## Default routing

### Presentation
image model -> React/SVG -> Mermaid

### Editable
React/SVG -> Mermaid

### Portable
Mermaid first

### Concept UI
image model -> React mock UI
