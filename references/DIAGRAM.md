# Diagram Rules

Use this file as the design source of truth for Diagram Studio.

Keep user-facing requests simple. Apply these rules internally when shaping output.

## Default mode

- presentation

## Output goals

- prioritize clarity over exhaustiveness
- prefer a polished diagram over a busy diagram
- keep the result usable across presentation, editable, and portable outputs

## Density

- default to medium-low density
- prefer 4 major zones over many equally weighted blocks
- reduce visible detail when the page feels crowded
- keep side panels supportive, not dominant

## Title hierarchy

- use an editorial headline with a neutral subtitle
- make the title block visible enough to orient the reader
- avoid uniform text sizing across the whole canvas

## Node cards

- use lighter cards with clear boundaries
- size nodes from content, not arbitrary symmetry
- allow multiline labels when they improve balance
- avoid fake product chrome unless the user explicitly wants concept UI mode

## Connectors

- keep connector styling lighter than card styling
- avoid letting arrows dominate the page
- use restrained semantic accents only when they improve comprehension

## Explainer panels

- default to compact explainer panels
- keep explainer content to 3 bullets unless the user asks for more
- integrate supporting notes into the composition instead of building a competing rail

## Color system

- use one primary accent with restrained semantic colors
- prefer calm backgrounds over dashboard-like saturation
- avoid rainbow category coloring and flashy gradient overload

## Style family mapping

- `editorial-technical`: research-paper and architecture-overview diagrams
- `product-minimal`: crisp product and docs visuals
- `operator-dark`: darker operator or systems views
- `neo-depth`: restrained 2.5D polish, not true 3D

## Claims and caution notes

- avoid implying equal support across every client or backend
- add a caution note when support varies by client, renderer, or export path
- do not overclaim verification or compatibility
