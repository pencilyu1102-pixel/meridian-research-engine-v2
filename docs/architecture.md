# Architecture

Meridian Research Engine 2.0 is organized as a workflow pack plus a small Python toolkit for the `v2.0.0-beta` initial release.

## Layers

| Layer | Directory | Role |
|---|---|---|
| Rules | `SKILL.md` | Core operating contract |
| Agents | `agents/` | Specialist analysis roles |
| Workflows | `workflows/` | Scenario-specific execution paths |
| Templates | `templates/` | Report and audit structures |
| Tools | `tools/` | Decimal-based calculation and gatekeeping utilities |
| Examples | `examples/` | Generic sample requests and fictional CSV inputs |
| Tests | `tests/` | Pytest verification |

## Design Principles

- Keep research conclusions separate from account actions.
- Keep company quality separate from valuation.
- Keep data reliability separate from data meaning.
- Preserve conflict and uncertainty.
- Use Decimal for financial calculations.
- Make every output reviewable and falsifiable.

## Tool Boundary

The Python tools calculate anchors, scenarios, costs, cards, and checks. They do not fetch brokerage data, place orders, or make automatic investment recommendations.
