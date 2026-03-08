# Real Estate Investment Analysis Agent - Architecture Design

## Multi-Agent Workflow Overview

System uses four specialized agents coordinated by an Orchestrator:

- **Orchestrator Agent**: Receives property address, validates input, dispatches work to other agents, aggregates results, returns final recommendation
- **Data Fetching Agent**: Collects property and market data from multiple public sources in parallel
- **Risk Assessment Agent**: Evaluates risk factors, runs in parallel with Data Fetching Agent
- **Calculation Agent**: Computes financial metrics and scenarios after data collection completes

Data Fetching and Risk Assessment run simultaneously. Calculation Agent waits for both to finish before executing.

---

## Orchestrator Agent

**Responsibilities:**
- Accept property address as input from user interface
- Validate address format and geocode if needed
- Dispatch Data Fetching Agent and Risk Assessment Agent in parallel
- Wait for both to complete their work
- Pass aggregated data to Calculation Agent
- Synthesize final recommendation with all supporting data
- Return structured JSON output to user
- Maintain human-in-the-loop interface for data corrections and user estimates
- Support future batch processing of multiple addresses

**Input Schema:**
```json
{
  "property_address": "string (required)",
  "user_overrides": "object (optional)"
}
```

**Output Schema:**
```json
{
  "recommendation": "object",
  "all_metrics": "object",
  "risk_assessment": "object",
  "data_sources": "array",
  "confidence_level": "string"
}
```

---

## Data Fetching Agent

**Responsibilities:**
- Collect property data using three parallel approaches simultaneously:
  - **Approach 1**: Query free APIs (Zillow, RentCast free tier, county assessor APIs)
  - **Approach 2**: Use LLM to parse and extract data from public web pages
  - **Approach 3**: Web scraping of public real estate websites
- Run all three sources in parallel — not sequential fallback
- Converge results by comparing outputs across all three sources
- Calculate confidence levels based on source agreement
- Flag discrepancies when sources conflict
- Trigger human-in-the-loop if all sources unavailable or conflict beyond tolerance
- Return all data with source attribution and timestamps

**Data to Collect:**
- Property details: address, square footage, lot size, year built, property type, bedrooms, bathrooms
- Tax history: annual property taxes for past 3 years
- Listing and valuation: current list price, estimated market value
- Rental data: rental comps, estimated monthly rental income
- Neighborhood: crime rates, school ratings, population trends, employment data, median income
- Amenities: proximity to transit, shopping, schools, parks

**Input Schema:**
```json
{
  "property_address": "string (required)"
}
```

**Output Schema:**
```json
{
  "property_data": "object",
  "market_data": "object",
  "data_sources": "array",
  "confidence_scores": "object",
  "discrepancies": "array (optional)",
  "missing_fields": "array (optional)"
}
```

---

## Risk Assessment Agent

**Responsibilities:**
- Run in parallel with Data Fetching Agent
- Assess market risk: economic indicators, local employment trends, population growth or decline
- Evaluate property risk: age, condition indicators, structural concerns if available
- Assess income/tenant risk: market rental rates, tenant quality indicators, vacancy rates
- Assign numerical risk scores for each category (1–10 scale, 10 = highest risk)
- Provide qualitative narrative for each risk category
- Flag data gaps affecting confidence in risk scores
- Return all assessments with source attribution

**Input Schema:**
```json
{
  "property_address": "string",
  "property_data": "object",
  "market_data": "object"
}
```

**Output Schema:**
```json
{
  "market_risk_score": "number (1-10)",
  "property_risk_score": "number (1-10)",
  "income_risk_score": "number (1-10)",
  "overall_risk_score": "number (1-10)",
  "risk_narratives": "object",
  "confidence_level": "number (0-1)",
  "missing_data_impacts": "array"
}
```

---

## Calculation Agent

**Responsibilities:**
- Receive converged property and market data from Orchestrator
- Calculate institutional metrics: cap rate, IRR, cash-on-cash return, equity multiple, DSCR
- Run best-case scenario with optimistic assumptions (higher rents, lower expenses, faster appreciation)
- Run worst-case scenario with conservative assumptions (lower rents, higher expenses, slower appreciation)
- Apply weighted scoring across all metrics (weights configurable by user)
- Identify missing critical inputs and flag to Orchestrator for human-in-the-loop
- Return full calculation breakdown with formulas and inputs used
- Never estimate or hallucinate missing data — flag as unavailable instead

**Calculation Formulas:**
- **Cap Rate**: (Net Operating Income / Property Value) × 100
- **IRR**: Internal rate of return over investment horizon
- **Cash-on-Cash Return**: (Annual Cash Flow / Total Cash Invested) × 100
- **Equity Multiple**: Total Cash Returned / Total Cash Invested
- **DSCR**: Net Operating Income / Annual Debt Service

**Input Schema:**
```json
{
  "property_data": "object",
  "market_data": "object",
  "financial_assumptions": "object",
  "user_weights": "object (optional)"
}
```

**Output Schema:**
```json
{
  "cap_rate": "number",
  "irr": "number",
  "cash_on_cash_return": "number",
  "equity_multiple": "number",
  "dscr": "number",
  "best_case_scenario": "object",
  "worst_case_scenario": "object",
  "calculation_breakdown": "array",
  "missing_inputs": "array (optional)"
}
```

---

## Data Contracts and JSON Communication

- All inter-agent communication uses JSON format with strict schema validation
- Each agent validates incoming JSON against defined schema before processing
- All data includes source attribution and collection timestamp
- Error responses include failure reason and list of missing fields
- Orchestrator is the single coordination point — agents do not communicate directly with each other

**Communication Flow:**
1. User provides property address to Orchestrator
2. Orchestrator validates address and dispatches Data Fetching and Risk Assessment agents in parallel
3. Data Fetching Agent collects from three sources simultaneously and converges results
4. Risk Assessment Agent evaluates risk factors using available data
5. Both agents return JSON payloads to Orchestrator
6. Orchestrator waits for both to complete, then triggers Calculation Agent
7. Calculation Agent processes data and returns metrics
8. Orchestrator aggregates all results and generates final recommendation
9. Final output returned to user with all supporting data and sources

---

## Error Handling and Graceful Degradation

- If a single data source is unavailable, agent attempts other sources before escalating
- If critical data completely unavailable from all sources, trigger human-in-the-loop for user input
- If data sources conflict beyond tolerance threshold, present discrepancy to user and request clarification
- If critical metric cannot be calculated due to missing inputs, flag as unreliable and request user input
- System never generates or estimates data when sources are unavailable
- Partial analysis is acceptable — output clearly indicates which metrics are reliable, estimated, or missing
- All errors surfaced to user with clear explanation of what is missing and why

---

## Modular Agent Design and Independent Testability

Each agent must be designed as an isolated, independently testable module with clear input and output contracts.

**Requirements:**
- Test each agent in isolation with mock data before integration
- Validate each agent against its defined JSON schema independently
- Bugs must be isolatable to a single agent without requiring full system run
- Agents can be swapped or updated without breaking the rest of the system

**Testing Hierarchy:**
1. Unit test individual agents with mock inputs
2. Integration test agent-to-agent communication via Orchestrator
3. End-to-end system testing with real or realistic data

---

## Future Extensibility

- Design Orchestrator to handle batch processing of multiple property addresses
- Support regional or ZIP code inputs that spawn multiple sub-orchestrators
- Implement property ranking across batch results by investment opportunity score
- Prepare architecture for transaction automation: loan applications, price negotiations, contract review
- Ensure agents can operate independently or as part of a larger investment workflow
- Design for easy addition of new data sources or new financial metrics

---

## Validation and Testing Strategy

- Backtest Analyst recommendations against historical property data with known outcomes
- Compare Analyst recommendations versus actual investment returns over time
- Measure whether top-ranked properties outperform bottom-ranked properties
- Iterate on metric weights and confidence thresholds based on validation results
- Document assumptions used in backtesting and update as new data becomes available
