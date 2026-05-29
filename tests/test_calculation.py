from __future__ import annotations

from real_estate_investor.calculation import CalculationAgent


def test_dscr_none_for_all_cash_purchase():
    property_data = {
        "current_list_price": 300000,
        "tax_history": [{"year": 2024, "amount": 3600}],
    }
    market_data = {"rental_estimate_low": 1800, "rental_estimate_high": 2100}
    assumptions = {
        "down_payment_percent": 100,
        "mortgage_rate": 6.0,
        "loan_term_years": 30,
        "insurance_estimate_annual": 1200,
        "maintenance_reserve_percent": 5,
        "vacancy_assumption": 5,
        "investment_horizon_years": 10,
        "appreciation_rate": 3.0,
    }
    result = CalculationAgent().calculate(property_data, market_data, assumptions)
    assert result.dscr is None
    assert any("all-cash" in item for item in result.missing_inputs)
