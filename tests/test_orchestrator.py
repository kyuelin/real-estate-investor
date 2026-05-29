from __future__ import annotations

import pytest

from real_estate_investor.orchestrator import RealEstateOrchestrator


def test_orchestrator_returns_required_top_level_fields():
    result = RealEstateOrchestrator().analyze("123 Main St, Springfield, IL")
    for field in (
        "property_address",
        "recommendation_label",
        "recommendation_score",
        "overall_confidence",
        "metrics",
        "risk_assessment",
        "weights_applied",
        "data_sources",
        "data_gaps",
        "user_inputs",
        "calculation_breakdown",
        "methodology_notes",
    ):
        assert field in result


def test_user_override_is_tagged_in_output():
    result = RealEstateOrchestrator().analyze(
        "123 Main St, Springfield, IL",
        user_overrides={"crime_rate": 9.0},
    )
    assert any(item["field"] == "crime_rate" for item in result["user_inputs"])
    crime_source = next(item for item in result["data_sources"] if item["field_name"] == "crime_rate")
    assert crime_source["user_override"] is True


def test_invalid_weight_total_is_rejected():
    with pytest.raises(ValueError, match="weights must sum to 1.0"):
        RealEstateOrchestrator().analyze(
            "123 Main St, Springfield, IL",
            user_weights={
                "cap_rate_weight": 0.2,
                "irr_weight": 0.2,
                "cash_on_cash_weight": 0.2,
                "equity_multiple_weight": 0.2,
                "dscr_weight": 0.2,
                "risk_score_weight": 0.2,
            },
        )


def test_missing_metric_renormalizes_weights():
    result = RealEstateOrchestrator().analyze(
        "123 Main St, Springfield, IL",
        financial_assumptions={"investment_horizon_years": None},
    )
    assert "irr_weight" not in result["weights_applied"]
