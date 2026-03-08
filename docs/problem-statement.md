# Real Estate Investment Analysis Agent - Problem Statement

## Overview

Build an AI agent system called the **Real Estate Investment Analyst** that evaluates residential real estate properties for investment potential. The system automatically gathers data from public sources, calculates institutional-grade financial metrics, and provides transparent, quantified investment recommendations.

---

## Inputs

- Primary: Single residential property address provided by the user
- Optional: User-provided data overrides or estimates to fill data gaps

---

## Outputs

- Quantified investment recommendation with confidence score
- All calculated financial metrics with full methodology transparency
- Best-case and worst-case scenario analysis
- Risk assessment across market, property, and income dimensions
- Complete source attribution for every data point used
- List of data gaps and their impact on recommendation confidence

---

## Core Requirements

- Multi-agent architecture with Orchestrator coordinating specialized agents
- Data Fetching and Risk Assessment agents run in parallel
- Calculation Agent executes after data collection completes
- Open source framework for multi-agent orchestration (e.g., LangGraph)
- Proof of concept validates logic with mock data before implementing live data sources
- All agents designed as isolated, independently testable modules
- System never hallucinates or estimates missing data — flags gaps instead

---

## Metrics to Calculate

- **Cap Rate**: Net Operating Income / Property Value × 100
- **IRR**: Internal Rate of Return over investment horizon
- **Cash-on-Cash Return**: Annual Cash Flow / Total Cash Invested × 100
- **Equity Multiple**: Total Cash Returned / Total Cash Invested
- **DSCR**: Debt Service Coverage Ratio (NOI / Annual Debt Service)
- **Best-Case Scenario**: All metrics recalculated with optimistic assumptions
- **Worst-Case Scenario**: All metrics recalculated with conservative assumptions

---

## Agent Roles

- **Orchestrator Agent**: Accepts property address, validates input, dispatches agents, aggregates results, returns final recommendation
- **Data Fetching Agent**: Gathers property, market, and neighborhood data from three parallel sources (APIs, LLM parsing, web scraping)
- **Risk Assessment Agent**: Evaluates market risk, property risk, and income/tenant risk
- **Calculation Agent**: Computes all financial metrics, scenarios, and weighted scoring

---

## Data Sources

- Free APIs: Zillow, RentCast free tier, county assessor APIs
- LLM-parsed public web pages: Realtor.com, Apartments.com, and similar
- Web scraping: Public real estate and neighborhood data sites
- User input: When sources are unavailable or conflict beyond acceptable tolerance

---

## Success Criteria

- System accepts a property address and returns all required financial metrics
- Every data point is tagged with its source and confidence level
- All calculations are transparent with formulas and inputs visible
- System handles missing data gracefully without hallucination
- Recommendations can be backtested against historical property outcomes
- User can tune metric weights based on their investment priorities
