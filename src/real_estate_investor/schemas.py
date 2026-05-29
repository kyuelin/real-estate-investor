from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceObservation:
    source_type: str
    source_name: str
    value: Any
    timestamp: str


@dataclass
class FieldAttribution:
    field_name: str
    value: Any
    sources: list[SourceObservation]
    confidence_level: str
    confidence_rationale: str
    discrepancies: list[Any] = field(default_factory=list)
    user_override: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataFetchResult:
    property_data: dict[str, Any]
    market_data: dict[str, Any]
    data_sources: list[FieldAttribution]
    confidence_scores: dict[str, str]
    discrepancies: list[dict[str, Any]] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["data_sources"] = [source.to_dict() for source in self.data_sources]
        return payload


@dataclass
class RiskAssessmentResult:
    market_risk_score: int
    market_risk_narrative: str
    property_risk_score: int
    property_risk_narrative: str
    income_risk_score: int
    income_risk_narrative: str
    overall_risk_score: float
    confidence_level: float
    missing_data_impacts: list[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CalculationResult:
    cap_rate: float | None
    irr: float | None
    cash_on_cash_return: float | None
    equity_multiple: float | None
    dscr: float | None
    net_operating_income: float | None
    annual_cash_flow: float | None
    total_cash_invested: float | None
    best_case_scenario: dict[str, Any]
    worst_case_scenario: dict[str, Any]
    calculation_breakdown: list[dict[str, Any]]
    missing_inputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
