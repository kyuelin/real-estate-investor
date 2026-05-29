from __future__ import annotations

from real_estate_investor.data_fetching import DataFetchingAgent


def test_data_sources_are_field_attributions():
    result = DataFetchingAgent().fetch("123 Main St, Springfield, IL")
    assert result.data_sources
    first = result.data_sources[0].to_dict()
    assert "field_name" in first
    assert "sources" in first
    assert isinstance(first["sources"], list)


def test_unknown_address_uses_default_fixture_with_low_confidence():
    result = DataFetchingAgent().fetch("999 Unknown Way")
    assert result.property_data["current_list_price"] == 250000
    assert result.confidence_scores["current_list_price"] == "low"
