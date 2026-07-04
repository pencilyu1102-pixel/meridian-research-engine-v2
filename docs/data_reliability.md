# Data Reliability

Data reliability engineering prevents weak data from creating false confidence.

## Source Tiers

| Tier | Source Type | Typical Use |
|---|---|---|
| S | Official filings, regulator data, official company releases | Can support formal conclusions if current and correctly interpreted |
| A | Company presentations, earnings calls, verified exchange data | Useful with context and timestamp |
| B | Reputable financial data vendors or major media | Useful when definitions are clear |
| C | Secondary commentary, transformed estimates, unclear screenshots | Usually only supports observation |
| D | Unknown, stale, broken, or unverifiable sources | Should not support formal conclusions |

## Required Metadata

- Source.
- Source tier.
- Timestamp.
- Unit.
- Currency.
- Accounting basis.
- Period basis.
- Conflict status.
- Whether the data can enter the conclusion.

## Important Rule

Reliable data does not automatically create correct meaning. Every key data point still needs a Data Meaning Block.
