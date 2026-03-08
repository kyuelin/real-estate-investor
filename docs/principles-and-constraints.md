# Real Estate Investment Analysis Agent - Principles and Constraints

## Open Source Framework Requirement

- Use only open source frameworks and libraries for core implementation
- No proprietary or commercial-only dependencies in critical path
- Framework must support multi-agent orchestration with state management
- Recommended: LangGraph (state machine-based, agent-oriented, open source)

---

## Human-in-the-Loop Triggers During Data Collection

- If data sources disagree beyond acceptable tolerance, flag discrepancy and request user input
- If required data is completely unavailable from all sources, request user estimation
- Never generate or hallucinate missing data to fill gaps
- User provides clarification or estimates; analysis resumes with updated data tagged as user-provided
- Future phases: add human approval gates for transaction actions (loan applications, negotiations, contract review)

---

## Convergence-Based Data Validation

- Collect data from all three sources in parallel — not sequential fallback
- Sources: free APIs, LLM parsing of web content, web scraping
- Cross-validate outputs across all three sources
- Calculate agreement levels and assign confidence scores based on alignment
- Surface discrepancies and agreement patterns to user
- Confidence levels: High (all 3 agree), Medium (2 agree), Low (sources conflict or only 1 available)

---

## Full Source Transparency

- Every data point in final output must identify its source: which API, which website, which scraper
- Include confidence score for each data point based on source agreement
- Include data collection timestamp for each field
- Flag any user-provided inputs separately from system-collected data
- User must be able to trace any metric back to its origin, formula, and methodology

---

## No Hallucination or Made-Up Metrics

- If data cannot be found or validated, flag as unavailable or uncertain — do not estimate
- Do not generate synthetic data to fill gaps under any circumstances
- Apply this rule across all agents: Data Fetching, Risk Assessment, Calculation
- Gracefully degrade output rather than fabricate metrics
- Better to return incomplete analysis with confidence flags than confident but false recommendations
- All assumptions used in calculations must be explicitly stated and visible

---

## Graceful Degradation

- System operates with partial data rather than failing completely
- Missing data triggers human-in-the-loop, not system error or failure
- Output clearly indicates which metrics are reliable, which are estimated, which are missing
- Recommendation confidence score adjusts based on data completeness
- User always sees what's solid, what's uncertain, and what's missing

---

## Modular Agent Design and Independent Testability

- Each agent must be designed as an isolated, independently testable module
- Each agent must have clearly defined input and output contracts (JSON schemas)
- Test each agent in isolation with mock data before integrating into multi-agent system
- Bugs must be isolatable to a single agent without running the full system
- Agents can be swapped or updated without breaking the rest of the system

**Testing Hierarchy:**
1. Unit test individual agents with mock inputs and expected outputs
2. Integration test agent-to-agent communication through Orchestrator
3. End-to-end system testing with real or realistic property data

---

## Model Agnostic Design

- All specifications written to work with any LLM provider (Claude, GPT, Llama, etc.)
- No model-specific syntax, features, or API patterns in core logic
- Architecture and agent logic independent of specific LLM choice
- Support swapping LLM providers without changing core architecture

---

## Cost Management

- Prioritize free tiers of public APIs to minimize costs
- Batch API calls where possible to reduce usage
- Use mock data in POC phase to validate logic before incurring API or LLM costs
- Monitor and log API usage per property analysis
- LLM parsing calls used only when API and scraping sources are insufficient
