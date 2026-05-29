from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from real_estate_investor.calculation import CalculationAgent
from real_estate_investor.data_fetching import DataFetchingAgent
from real_estate_investor.risk_assessment import RiskAssessmentAgent

DEFAULT_WEIGHTS = {
    "cap_rate_weight": 0.20,
    "irr_weight": 0.25,
    "cash_on_cash_weight": 0.20,
    "equity_multiple_weight": 0.15,
    "dscr_weight": 0.10,
    "risk_score_weight": 0.10,
}

DEFAULT_ASSUMPTIONS = {
    "mortgage_rate": 6.5,
    "loan_term_years": 30,
    "down_payment_percent": 20,
    "property_tax_rate": 1.2,
    "insurance_estimate_annual": 1800,
    "maintenance_reserve_percent": 6,
    "vacancy_assumption": 5,
    "appreciation_rate": 3.0,
    "investment_horizon_years": 10,
}


class RealEstateOrchestrator:
    def __init__(
        self,
        data_fetching_agent: DataFetchingAgent | None = None,
        risk_agent: RiskAssessmentAgent | None = None,
        calculation_agent: CalculationAgent | None = None,
    ) -> None:
        self.data_fetching_agent = data_fetching_agent or DataFetchingAgent()
        self.risk_agent = risk_agent or RiskAssessmentAgent()
        self.calculation_agent = calculation_agent or CalculationAgent()

    def analyze(
        self,
        property_address: str,
        user_overrides: dict[str, Any] | None = None,
        financial_assumptions: dict[str, Any] | None = None,
        user_weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        if not property_address or not property_address.strip():
            raise ValueError("property_address is required")

        assumptions = dict(DEFAULT_ASSUMPTIONS)
        assumptions.update(financial_assumptions or {})
        weights = dict(DEFAULT_WEIGHTS)
        if user_weights:
            weights.update(user_weights)
        self._validate_weights(weights)

        with ThreadPoolExecutor(max_workers=2) as pool:
            fetch_future = pool.submit(self.data_fetching_agent.fetch, property_address, user_overrides)
            pre_risk_future = pool.submit(self.risk_agent.pre_assess, property_address)
            fetch_result = fetch_future.result()
            baseline = pre_risk_future.result()

        risk_result = self.risk_agent.assess(
            property_address=property_address,
            property_data=fetch_result.property_data,
            market_data=fetch_result.market_data,
            baseline=baseline,
        )
        calc_result = self.calculation_agent.calculate(
            property_data=fetch_result.property_data,
            market_data=fetch_result.market_data,
            assumptions=assumptions,
        )

        score, adjusted_weights, scored_metrics = self._recommendation_score(calc_result.to_dict(), risk_result.overall_risk_score, weights)
        confidence = self._overall_confidence(fetch_result, risk_result, calc_result.to_dict())
        label = self._label(score)
        missing = (
            [f"data:{field}" for field in fetch_result.missing_fields]
            + [f"risk:{item['field']}" for item in risk_result.missing_data_impacts]
            + [f"calc:{item}" for item in calc_result.missing_inputs]
        )
        user_inputs = [
            {"field": source.field_name, "value": source.value}
            for source in fetch_result.data_sources
            if source.user_override
        ]

        return {
            "property_address": property_address,
            "recommendation_label": label,
            "recommendation_score": score,
            "overall_confidence": confidence,
            "calculation_date": datetime.now(timezone.utc).isoformat(),
            "executive_summary": (
                f"{label.replace('_', ' ').title()} for {property_address} with score {score if score is not None else 'N/A'} "
                f"and confidence {confidence} based on available market and financial signals."
            ),
            "metrics": calc_result.to_dict(),
            "scenarios": {
                "best_case_scenario": calc_result.best_case_scenario,
                "worst_case_scenario": calc_result.worst_case_scenario,
            },
            "risk_assessment": risk_result.to_dict(),
            "weights_applied": adjusted_weights,
            "data_sources": [source.to_dict() for source in fetch_result.data_sources],
            "data_gaps": [{"field": gap, "impact_on_analysis": "Reduced confidence"} for gap in sorted(set(missing))],
            "user_inputs": user_inputs,
            "calculation_breakdown": calc_result.calculation_breakdown,
            "methodology_notes": (
                f"Scored metrics: {', '.join(scored_metrics)}. Missing metrics were excluded and remaining weights were renormalized."
            ),
        }

    def _validate_weights(self, weights: dict[str, float]) -> None:
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1.0; got {total:.6f}")

    def _recommendation_score(
        self,
        metrics: dict[str, Any],
        overall_risk: float,
        weights: dict[str, float],
    ) -> tuple[float | None, dict[str, float], list[str]]:
        metric_inputs = {
            "cap_rate_weight": self._scale(metrics.get("cap_rate"), 0, 12),
            "irr_weight": self._scale(metrics.get("irr"), 0, 20),
            "cash_on_cash_weight": self._scale(metrics.get("cash_on_cash_return"), -10, 20),
            "equity_multiple_weight": self._scale(metrics.get("equity_multiple"), 0.8, 3.0),
            "dscr_weight": self._scale(metrics.get("dscr"), 0.8, 2.0),
            "risk_score_weight": self._scale(10 - overall_risk, 0, 10),
        }

        available_weights = {key: weights[key] for key, value in metric_inputs.items() if value is not None}
        if not available_weights:
            return None, {}, []
        total_available = sum(available_weights.values())
        adjusted_weights = {key: round(value / total_available, 6) for key, value in available_weights.items()}
        score = 0.0
        for key, adjusted_weight in adjusted_weights.items():
            score += metric_inputs[key] * adjusted_weight
        scored = [key.replace("_weight", "") for key in adjusted_weights]
        return round(score * 100, 2), adjusted_weights, scored

    def _overall_confidence(self, fetch_result: Any, risk_result: Any, metrics: dict[str, Any]) -> float:
        total_fields = len(fetch_result.confidence_scores)
        strong_fields = sum(
            1
            for level in fetch_result.confidence_scores.values()
            if level in {"high", "medium"}
        )
        data_conf = (strong_fields / total_fields) if total_fields else 0.0
        metric_values = ["cap_rate", "irr", "cash_on_cash_return", "equity_multiple", "dscr"]
        available_metric_ratio = sum(1 for metric in metric_values if metrics.get(metric) is not None) / len(metric_values)
        return round((data_conf * 0.45) + (risk_result.confidence_level * 0.25) + (available_metric_ratio * 0.3), 2)

    def _scale(self, value: float | None, low: float, high: float) -> float | None:
        if value is None:
            return None
        if high == low:
            return 0.0
        clipped = max(low, min(high, value))
        return (clipped - low) / (high - low)

    def _label(self, score: float | None) -> str:
        if score is None:
            return "hold"
        if score >= 80:
            return "strong_buy"
        if score >= 65:
            return "buy"
        if score >= 50:
            return "hold"
        if score >= 35:
            return "pass"
        return "avoid"
