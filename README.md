# Real Estate Investor

Status: actively maintained.

This project implements a functional MVP of a multi-agent real-estate investment analyst. It runs deterministic mock-source data collection, converges source agreement with confidence levels, computes investment metrics, performs risk scoring, and returns a transparent recommendation.

See `docs/` for product requirements and architecture specs.

## Repository contents

- `src/real_estate_investor/orchestrator.py` — orchestrates the agent workflow and final recommendation
- `src/real_estate_investor/data_fetching.py` — parallel-source mock data convergence and attribution
- `src/real_estate_investor/risk_assessment.py` — market/property/income risk scoring
- `src/real_estate_investor/calculation.py` — cap rate, IRR, cash-on-cash, equity multiple, DSCR, scenarios
- `src/real_estate_investor/cli.py` — runnable CLI entry point
- `data/mock/properties.json` — deterministic source fixtures
- `tests/` — unit/integration/CLI tests
- `README.md` — project overview
- `docs/` — problem, architecture, schemas, and constraints

## Maturity review

**Maturity:** Functional MVP with agent modules, orchestration, CLI, and tests.

**What remains to make this a functional application:**
- Replace mock data sources with real API/scraping connectors.
- Add persistent storage and human-review workflows for data conflicts.
- Add a UI (web or notebook) for non-CLI usage.
- Add live backtesting against historical outcomes.

## Usage

```bash
python -m real_estate_investor.cli analyze --address "123 Main St, Springfield, IL"
```
