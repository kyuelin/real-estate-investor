from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from real_estate_investor.schemas import DataFetchResult, FieldAttribution, SourceObservation

PROPERTY_FIELDS = {
    "address",
    "square_footage",
    "lot_size",
    "year_built",
    "property_type",
    "bedrooms",
    "bathrooms",
    "current_list_price",
    "estimated_market_value",
    "tax_history",
    "property_condition",
    "hoa_fees_annual",
    "number_of_units",
}

MARKET_FIELDS = {
    "rental_estimate_low",
    "rental_estimate_high",
    "comparable_sales",
    "crime_rate",
    "school_rating",
    "population_trend",
    "unemployment_rate",
    "median_income",
    "vacancy_rate",
    "proximity_to_transit",
    "proximity_to_shopping",
}

EXPECTED_FIELDS = PROPERTY_FIELDS | MARKET_FIELDS
NUMERIC_TOLERANCE = 0.05


class DataFetchingAgent:
    def __init__(self, fixture_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[2] / "data" / "mock" / "properties.json"
        self.fixture_path = Path(fixture_path) if fixture_path else default_path
        self._fixtures = json.loads(self.fixture_path.read_text(encoding="utf-8"))

    def fetch(self, property_address: str, user_overrides: dict[str, Any] | None = None) -> DataFetchResult:
        profile = self._fixtures.get(property_address) or self._fixtures.get("default", {})
        sources = profile.get("sources", {})
        timestamp = datetime.now(timezone.utc).isoformat()

        field_values: dict[str, list[tuple[str, Any]]] = {}
        for source_name, source_payload in sources.items():
            for field_name, value in source_payload.items():
                field_values.setdefault(field_name, []).append((source_name, value))

        discrepancies: list[dict[str, Any]] = []
        data_sources: list[FieldAttribution] = []
        confidence_scores: dict[str, str] = {}

        for field_name, values in field_values.items():
            chosen_value, confidence_level, confidence_rationale, field_discrepancies = self._converge(values)
            user_override = False
            if user_overrides and field_name in user_overrides:
                chosen_value = user_overrides[field_name]
                confidence_level = "low"
                confidence_rationale = "User override provided"
                user_override = True
                field_discrepancies = []

            if field_discrepancies:
                discrepancies.append({"field": field_name, "values": field_discrepancies})

            observation = FieldAttribution(
                field_name=field_name,
                value=chosen_value,
                confidence_level=confidence_level,
                confidence_rationale=confidence_rationale,
                discrepancies=field_discrepancies,
                user_override=user_override,
                sources=[
                    SourceObservation(
                        source_type=self._source_type(source_name),
                        source_name=source_name,
                        value=value,
                        timestamp=timestamp,
                    )
                    for source_name, value in values
                ],
            )
            data_sources.append(observation)
            confidence_scores[field_name] = confidence_level

        missing_fields = sorted(field for field in EXPECTED_FIELDS if field not in field_values and not (user_overrides and field in user_overrides))

        property_data = {
            entry.field_name: entry.value
            for entry in data_sources
            if entry.field_name in PROPERTY_FIELDS
        }
        market_data = {
            entry.field_name: entry.value
            for entry in data_sources
            if entry.field_name in MARKET_FIELDS
        }

        if user_overrides:
            for key, value in user_overrides.items():
                if key not in property_data and key in PROPERTY_FIELDS:
                    property_data[key] = value
                if key not in market_data and key in MARKET_FIELDS:
                    market_data[key] = value
                if key not in field_values:
                    data_sources.append(
                        FieldAttribution(
                            field_name=key,
                            value=value,
                            confidence_level="low",
                            confidence_rationale="User supplied input due to missing source data",
                            discrepancies=[],
                            user_override=True,
                            sources=[
                                SourceObservation(
                                    source_type="user_input",
                                    source_name="user_override",
                                    value=value,
                                    timestamp=timestamp,
                                )
                            ],
                        )
                    )
                    confidence_scores[key] = "low"

        return DataFetchResult(
            property_data=property_data,
            market_data=market_data,
            data_sources=data_sources,
            confidence_scores=confidence_scores,
            discrepancies=discrepancies,
            missing_fields=missing_fields,
        )

    def _converge(self, values: list[tuple[str, Any]]) -> tuple[Any, str, str, list[Any]]:
        raw_values = [value for _, value in values]
        if len(values) == 1:
            return raw_values[0], "low", "Only one source available", []

        if self._agree(raw_values):
            if len(values) >= 3:
                return raw_values[0], "high", "All three sources agree", []
            return raw_values[0], "medium", "Two sources agree", []

        return raw_values[0], "low", "Sources conflict beyond tolerance", raw_values

    def _agree(self, values: list[Any]) -> bool:
        first = values[0]
        if isinstance(first, (int, float)):
            if first == 0:
                return all(value == 0 for value in values)
            return all(
                isinstance(value, (int, float)) and abs(value - first) / abs(first) <= NUMERIC_TOLERANCE
                for value in values[1:]
            )
        return all(str(value).strip().lower() == str(first).strip().lower() for value in values[1:])

    def _source_type(self, source_name: str) -> str:
        if source_name.startswith("api"):
            return "api"
        if source_name.startswith("llm"):
            return "llm_parse"
        if source_name.startswith("scrape"):
            return "web_scrape"
        return "api"
