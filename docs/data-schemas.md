# Real Estate Investment Analysis Agent - Data Schemas and Specifications

## Property Data Schema

Collected by Data Fetching Agent. All fields include source attribution.

```json
{
  "address": "string (required)",
  "square_footage": "integer (optional) — building area in sq ft",
  "lot_size": "integer (optional) — lot area in sq ft",
  "year_built": "integer (optional)",
  "property_type": "enum (required): single_family | multi_family | condo | townhouse",
  "bedrooms": "integer (optional)",
  "bathrooms": "number (optional)",
  "current_list_price": "decimal USD (required)",
  "estimated_market_value": "decimal USD (optional)",
  "tax_history": "array of { year: integer, amount: decimal USD } (optional)",
  "property_condition": "enum (optional): excellent | good | fair | poor",
  "hoa_fees_annual": "decimal USD (optional)",
  "number_of_units": "integer (optional) — for multi-family only"
}
```

---

## Market and Neighborhood Data Schema

```json
{
  "rental_estimate_low": "decimal USD monthly (optional)",
  "rental_estimate_high": "decimal USD monthly (optional)",
  "comparable_sales": "array of { address: string, price: decimal, sale_date: string } (optional)",
  "crime_rate": "decimal (optional) — crimes per 1000 residents",
  "school_rating": "decimal (optional) — scale 0 to 10",
  "population_trend": "enum (optional): growing | stable | declining",
  "unemployment_rate": "decimal (optional) — local area percentage",
  "median_income": "decimal USD (optional) — area median household income",
  "vacancy_rate": "decimal (optional) — local market vacancy percentage",
  "proximity_to_transit": "decimal (optional) — miles to nearest transit",
  "proximity_to_shopping": "decimal (optional) — miles to nearest shopping"
}
```

---

## Financial Assumptions Schema

User-configurable inputs used by Calculation Agent.

```json
{
  "mortgage_rate": "decimal percentage (required) — annual interest rate",
  "loan_term_years": "integer (required) — e.g. 30",
  "down_payment_percent": "decimal percentage (required) — e.g. 20",
  "property_tax_rate": "decimal percentage (optional) — annual as % of value",
  "insurance_estimate_annual": "decimal USD (optional)",
  "maintenance_reserve_percent": "decimal percentage (optional) — % of rental income",
  "vacancy_assumption": "decimal percentage (optional) — assumed vacancy for calculations",
  "appreciation_rate": "decimal percentage (optional) — assumed annual appreciation",
  "inflation_rate": "decimal percentage (optional) — assumed annual inflation",
  "investment_horizon_years": "integer (optional) — holding period for IRR calculation"
}
```

---

## Calculated Metrics Schema

Output of Calculation Agent.

```json
{
  "cap_rate": "decimal — percentage",
  "irr": "decimal — percentage over investment horizon",
  "cash_on_cash_return": "decimal — percentage",
  "equity_multiple": "decimal — multiplier (e.g. 1.8 = 1.8x)",
  "dscr": "decimal — ratio (e.g. 1.25)",
  "net_operating_income": "decimal USD — annual",
  "annual_cash_flow": "decimal USD",
  "total_cash_invested": "decimal USD",
  "best_case_scenario": {
    "cap_rate": "decimal",
    "irr": "decimal",
    "cash_on_cash_return": "decimal",
    "equity_multiple": "decimal",
    "dscr": "decimal",
    "assumptions": "object — optimistic inputs used"
  },
  "worst_case_scenario": {
    "cap_rate": "decimal",
    "irr": "decimal",
    "cash_on_cash_return": "decimal",
    "equity_multiple": "decimal",
    "dscr": "decimal",
    "assumptions": "object — conservative inputs used"
  },
  "calculation_breakdown": "array of { metric: string, formula: string, inputs: object, result: decimal }"
}
```

---

## Risk Assessment Schema

Output of Risk Assessment Agent.

```json
{
  "market_risk_score": "integer 1-10 (10 = highest risk)",
  "market_risk_narrative": "string",
  "property_risk_score": "integer 1-10",
  "property_risk_narrative": "string",
  "income_risk_score": "integer 1-10",
  "income_risk_narrative": "string",
  "overall_risk_score": "decimal — weighted average of all risk scores",
  "confidence_level": "decimal 0-1 — based on data availability",
  "missing_data_impacts": "array of { field: string, impact: string }"
}
```

---

## Data Source Attribution Schema

Every data point returned by Data Fetching Agent must include this wrapper.

```json
{
  "field_name": "string — name of the data field",
  "value": "any — the actual data value",
  "sources": [
    {
      "source_type": "enum: api | llm_parse | web_scrape | user_input",
      "source_name": "string — e.g. Zillow, county_assessor, Apartments.com",
      "value": "any — value returned by this specific source",
      "timestamp": "string — ISO 8601 datetime"
    }
  ],
  "confidence_level": "enum: high | medium | low",
  "confidence_rationale": "string — e.g. all 3 sources agree, or sources conflict",
  "discrepancies": "array (optional) — list conflicting values if sources disagree",
  "user_override": "boolean (optional) — true if user provided this value manually"
}
```

---

## Final Recommendation Output Schema

Compiled and returned by Orchestrator Agent.

```json
{
  "property_address": "string",
  "recommendation_label": "enum: strong_buy | buy | hold | pass | avoid",
  "recommendation_score": "decimal 0-100 — weighted composite score",
  "overall_confidence": "decimal 0-1 — based on data completeness",
  "calculation_date": "string — ISO 8601 datetime",
  "executive_summary": "string — brief narrative of recommendation",
  "metrics": "object — all calculated metrics (cap rate, IRR, cash-on-cash, equity multiple, DSCR)",
  "scenarios": "object — best-case and worst-case with all metrics",
  "risk_assessment": "object — all risk scores and narratives",
  "weights_applied": "object — scoring weights used, tunable by user",
  "data_sources": "array — complete source attribution for every data point",
  "data_gaps": "array of { field: string, impact_on_analysis: string }",
  "user_inputs": "array — any data the user provided to fill gaps",
  "calculation_breakdown": "array — step-by-step formulas and inputs for each metric",
  "methodology_notes": "string — explanation of weighting logic and key assumptions"
}
```

---

## Scoring Weights Schema

User-configurable weights applied by Calculation Agent. Must sum to 1.0.

```json
{
  "cap_rate_weight": "decimal — default 0.20",
  "irr_weight": "decimal — default 0.25",
  "cash_on_cash_weight": "decimal — default 0.20",
  "equity_multiple_weight": "decimal — default 0.15",
  "dscr_weight": "decimal — default 0.10",
  "risk_score_weight": "decimal — default 0.10"
}
```

Default weights total 1.0. User can adjust based on investment priorities (e.g., prioritize cash flow vs. appreciation).
