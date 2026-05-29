from __future__ import annotations

from typing import Any

from real_estate_investor.schemas import RiskAssessmentResult


class RiskAssessmentAgent:
    def pre_assess(self, property_address: str) -> dict[str, Any]:
        # Lightweight pre-work so orchestration can parallelize while data fetch runs.
        return {
            "address_quality_score": 0.9 if len(property_address.strip()) > 8 else 0.5,
        }

    def assess(
        self,
        property_address: str,
        property_data: dict[str, Any],
        market_data: dict[str, Any],
        baseline: dict[str, Any] | None = None,
    ) -> RiskAssessmentResult:
        baseline = baseline or {}
        missing: list[dict[str, str]] = []

        market_score = 5
        crime = market_data.get("crime_rate")
        if crime is None:
            missing.append({"field": "crime_rate", "impact": "Market risk confidence reduced"})
        elif crime > 7:
            market_score += 2
        elif crime < 4:
            market_score -= 1

        unemployment = market_data.get("unemployment_rate")
        if unemployment is None:
            missing.append({"field": "unemployment_rate", "impact": "Market volatility unknown"})
        elif unemployment > 7:
            market_score += 1

        trend = market_data.get("population_trend")
        if trend is None:
            missing.append({"field": "population_trend", "impact": "Demand trend uncertain"})
        elif trend == "declining":
            market_score += 2
        elif trend == "growing":
            market_score -= 1

        property_score = 5
        year_built = property_data.get("year_built")
        if year_built is None:
            missing.append({"field": "year_built", "impact": "Age-related risk uncertain"})
        elif year_built < 1970:
            property_score += 2
        elif year_built >= 2005:
            property_score -= 1

        condition = property_data.get("property_condition")
        if condition is None:
            missing.append({"field": "property_condition", "impact": "Condition risk cannot be confirmed"})
        elif condition == "poor":
            property_score += 2
        elif condition == "excellent":
            property_score -= 1

        income_score = 5
        vacancy = market_data.get("vacancy_rate")
        if vacancy is None:
            missing.append({"field": "vacancy_rate", "impact": "Tenant demand uncertainty increases"})
        elif vacancy > 8:
            income_score += 2
        elif vacancy < 4:
            income_score -= 1

        rent_low = market_data.get("rental_estimate_low")
        rent_high = market_data.get("rental_estimate_high")
        if rent_low is None or rent_high is None:
            missing.append({"field": "rental_estimate_low/high", "impact": "Cashflow risk estimate is weaker"})
        elif rent_high - rent_low > 800:
            income_score += 1

        address_quality = baseline.get("address_quality_score", 0.5)
        if address_quality < 0.7:
            market_score += 1

        market_score = self._clamp(market_score)
        property_score = self._clamp(property_score)
        income_score = self._clamp(income_score)
        overall = round((market_score * 0.4) + (property_score * 0.3) + (income_score * 0.3), 2)

        expected_signals = 7
        confidence = round(max(0.2, min(1.0, (expected_signals - len(missing)) / expected_signals)), 2)

        return RiskAssessmentResult(
            market_risk_score=market_score,
            market_risk_narrative=f"Market risk for {property_address} estimated at {market_score}/10 based on crime, employment, and trend signals.",
            property_risk_score=property_score,
            property_risk_narrative=f"Property risk estimated at {property_score}/10 based on condition and build-year indicators.",
            income_risk_score=income_score,
            income_risk_narrative=f"Income risk estimated at {income_score}/10 based on rent spread and vacancy indicators.",
            overall_risk_score=overall,
            confidence_level=confidence,
            missing_data_impacts=missing,
        )

    def _clamp(self, score: int) -> int:
        return max(1, min(10, score))
