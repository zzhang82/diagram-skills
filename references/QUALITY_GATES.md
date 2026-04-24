# Quality Gates

Use these as maintainer-facing review gates.

The current runtime only enforces a small subset directly in code. Treat this file as the design and validation target while dedicated validators continue to expand.

## Core checks

- text overflow
- crowded cards
- too many major zones
- weak title or subtitle hierarchy
- connector dominance
- overuse of color
- side-panel weight that overpowers the diagram

## Output-fit checks

- presentation output should feel calm and intentional
- editable output should stay deterministic and inspectable
- portable output should preserve structure without pretending to be the most polished mode

## Accuracy checks

- tool and client labels should stay public and accurate
- support claims should not imply parity where support varies by client
- caution notes should appear when the output could be misunderstood as universally supported

## Escalation rule

- if the diagram is dense enough that readability and completeness conflict, choose readability and simplify
