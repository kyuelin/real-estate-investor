from __future__ import annotations

from typing import Any

from real_estate_investor.schemas import CalculationResult


class CalculationAgent:
    def calculate(
        self,
        property_data: dict[str, Any],
        market_data: dict[str, Any],
        assumptions: dict[str, Any],
    ) -> CalculationResult:
        missing_inputs: list[str] = []
        breakdown: list[dict[str, Any]] = []

        price = property_data.get("current_list_price")
        if price is None:
            missing_inputs.append("current_list_price is required for core metrics")
            return self._empty_result(missing_inputs)

        rent_low = market_data.get("rental_estimate_low")
        rent_high = market_data.get("rental_estimate_high")
        if rent_low is None or rent_high is None:
            missing_inputs.append("rental_estimate_low and rental_estimate_high are required for NOI")
            return self._empty_result(missing_inputs)

        monthly_rent = (rent_low + rent_high) / 2
        annual_gross_rent = monthly_rent * 12

        property_tax = self._property_tax(price, property_data, assumptions, missing_inputs)
        insurance = assumptions.get("insurance_estimate_annual")
        if insurance is None:
            insurance = 0.0
            missing_inputs.append("insurance_estimate_annual missing; NOI may be overstated")

        maintenance_pct = assumptions.get("maintenance_reserve_percent")
        if maintenance_pct is None:
            maintenance = 0.0
            missing_inputs.append("maintenance_reserve_percent missing; NOI may be overstated")
        else:
            maintenance = annual_gross_rent * (maintenance_pct / 100)

        vacancy_assumption = assumptions.get("vacancy_assumption")
        if vacancy_assumption is None:
            vacancy_loss = 0.0
            missing_inputs.append("vacancy_assumption missing; NOI may be overstated")
        else:
            vacancy_loss = annual_gross_rent * (vacancy_assumption / 100)

        operating_expenses = property_tax + insurance + maintenance + vacancy_loss
        noi = annual_gross_rent - operating_expenses
        breakdown.append(
            {
                "metric": "net_operating_income",
                "formula": "Annual Gross Rent - Operating Expenses",
                "inputs": {
                    "annual_gross_rent": annual_gross_rent,
                    "property_tax": property_tax,
                    "insurance": insurance,
                    "maintenance": maintenance,
                    "vacancy_loss": vacancy_loss,
                },
                "result": round(noi, 2),
            }
        )

        cap_rate = round((noi / price) * 100, 2) if price else None
        breakdown.append(
            {
                "metric": "cap_rate",
                "formula": "(NOI / Property Value) * 100",
                "inputs": {"noi": noi, "property_value": price},
                "result": cap_rate,
            }
        )

        down_payment_percent = assumptions.get("down_payment_percent")
        if down_payment_percent is None:
            missing_inputs.append("down_payment_percent required")
            return self._empty_result(missing_inputs, noi=noi, cap_rate=cap_rate, breakdown=breakdown)

        total_cash_invested = round(price * (down_payment_percent / 100), 2)
        annual_debt_service = self._annual_debt_service(price, assumptions, missing_inputs)
        if annual_debt_service is None:
            annual_cash_flow = None
            cash_on_cash = None
            dscr = None
        else:
            annual_cash_flow = round(noi - annual_debt_service, 2)
            cash_on_cash = (
                round((annual_cash_flow / total_cash_invested) * 100, 2)
                if total_cash_invested > 0
                else None
            )
            dscr = round(noi / annual_debt_service, 2) if annual_debt_service > 0 else None

        if annual_debt_service == 0:
            dscr = None
            missing_inputs.append("dscr unavailable for all-cash purchase with zero debt service")

        breakdown.extend(
            [
                {
                    "metric": "cash_on_cash_return",
                    "formula": "(Annual Cash Flow / Total Cash Invested) * 100",
                    "inputs": {
                        "annual_cash_flow": annual_cash_flow,
                        "total_cash_invested": total_cash_invested,
                    },
                    "result": cash_on_cash,
                },
                {
                    "metric": "dscr",
                    "formula": "NOI / Annual Debt Service",
                    "inputs": {"noi": noi, "annual_debt_service": annual_debt_service},
                    "result": dscr,
                },
            ]
        )

        irr, equity_multiple = self._equity_metrics(
            price=price,
            annual_cash_flow=annual_cash_flow,
            total_cash_invested=total_cash_invested,
            assumptions=assumptions,
            missing_inputs=missing_inputs,
        )

        scenarios = self._scenarios(
            noi=noi,
            annual_debt_service=annual_debt_service,
            total_cash_invested=total_cash_invested,
            price=price,
            assumptions=assumptions,
        )

        return CalculationResult(
            cap_rate=cap_rate,
            irr=irr,
            cash_on_cash_return=cash_on_cash,
            equity_multiple=equity_multiple,
            dscr=dscr,
            net_operating_income=round(noi, 2),
            annual_cash_flow=annual_cash_flow,
            total_cash_invested=total_cash_invested,
            best_case_scenario=scenarios["best"],
            worst_case_scenario=scenarios["worst"],
            calculation_breakdown=breakdown,
            missing_inputs=sorted(set(missing_inputs)),
        )

    def _property_tax(
        self,
        price: float,
        property_data: dict[str, Any],
        assumptions: dict[str, Any],
        missing_inputs: list[str],
    ) -> float:
        tax_history = property_data.get("tax_history") or []
        if tax_history:
            latest = sorted(tax_history, key=lambda item: item.get("year", 0))[-1]
            return float(latest.get("amount", 0.0))
        tax_rate = assumptions.get("property_tax_rate")
        if tax_rate is None:
            missing_inputs.append("property_tax_rate missing and no tax_history; property tax assumed 0")
            return 0.0
        return price * (tax_rate / 100)

    def _annual_debt_service(
        self,
        price: float,
        assumptions: dict[str, Any],
        missing_inputs: list[str],
    ) -> float | None:
        down = assumptions.get("down_payment_percent")
        if down is None:
            return None
        principal = price * (1 - (down / 100))
        if principal <= 0:
            return 0.0
        rate = assumptions.get("mortgage_rate")
        years = assumptions.get("loan_term_years")
        if rate is None or years is None:
            missing_inputs.append("mortgage_rate and loan_term_years required for debt service")
            return None
        monthly_rate = (rate / 100) / 12
        periods = int(years) * 12
        if monthly_rate == 0:
            payment = principal / periods
        else:
            payment = principal * (monthly_rate * (1 + monthly_rate) ** periods) / ((1 + monthly_rate) ** periods - 1)
        return round(payment * 12, 2)

    def _equity_metrics(
        self,
        price: float,
        annual_cash_flow: float | None,
        total_cash_invested: float,
        assumptions: dict[str, Any],
        missing_inputs: list[str],
    ) -> tuple[float | None, float | None]:
        horizon = assumptions.get("investment_horizon_years")
        appreciation_rate = assumptions.get("appreciation_rate")
        if horizon is None or appreciation_rate is None or annual_cash_flow is None:
            missing_inputs.append("IRR and equity multiple require investment_horizon_years, appreciation_rate, and annual_cash_flow")
            return None, None

        horizon = int(horizon)
        future_sale_value = price * ((1 + appreciation_rate / 100) ** horizon)
        total_return = (annual_cash_flow * horizon) + future_sale_value
        equity_multiple = round(total_return / total_cash_invested, 2) if total_cash_invested else None

        cashflows = [-total_cash_invested] + [annual_cash_flow] * horizon
        cashflows[-1] += future_sale_value
        irr = round(self._irr(cashflows) * 100, 2)
        return irr, equity_multiple

    def _irr(self, cashflows: list[float], iterations: int = 100) -> float:
        low = -0.99
        high = 1.0
        for _ in range(iterations):
            mid = (low + high) / 2
            npv = sum(cf / ((1 + mid) ** idx) for idx, cf in enumerate(cashflows))
            if npv > 0:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    def _scenarios(
        self,
        noi: float,
        annual_debt_service: float | None,
        total_cash_invested: float | None,
        price: float,
        assumptions: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        def run(multiplier_noi: float, multiplier_debt: float, label: str) -> dict[str, Any]:
            scenario_noi = noi * multiplier_noi
            scenario_debt = None if annual_debt_service is None else annual_debt_service * multiplier_debt
            scenario_cash_flow = None if scenario_debt is None else scenario_noi - scenario_debt
            return {
                "cap_rate": round((scenario_noi / price) * 100, 2) if price else None,
                "irr": None,
                "cash_on_cash_return": (
                    round((scenario_cash_flow / total_cash_invested) * 100, 2)
                    if scenario_cash_flow is not None and total_cash_invested
                    else None
                ),
                "equity_multiple": None,
                "dscr": round(scenario_noi / scenario_debt, 2) if scenario_debt and scenario_debt > 0 else None,
                "assumptions": {
                    "scenario": label,
                    "noi_multiplier": multiplier_noi,
                    "debt_multiplier": multiplier_debt,
                    "base_assumptions": assumptions,
                },
            }

        return {
            "best": run(1.1, 0.98, "best_case"),
            "worst": run(0.9, 1.02, "worst_case"),
        }

    def _empty_result(
        self,
        missing_inputs: list[str],
        noi: float | None = None,
        cap_rate: float | None = None,
        breakdown: list[dict[str, Any]] | None = None,
    ) -> CalculationResult:
        return CalculationResult(
            cap_rate=cap_rate,
            irr=None,
            cash_on_cash_return=None,
            equity_multiple=None,
            dscr=None,
            net_operating_income=round(noi, 2) if isinstance(noi, (int, float)) else None,
            annual_cash_flow=None,
            total_cash_invested=None,
            best_case_scenario={},
            worst_case_scenario={},
            calculation_breakdown=breakdown or [],
            missing_inputs=sorted(set(missing_inputs)),
        )
