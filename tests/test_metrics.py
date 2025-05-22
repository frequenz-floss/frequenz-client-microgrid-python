# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sample class and related classes."""

from frequenz.client.microgrid.metrics import AggregatedMetricValue, AggregationMethod


def test_aggregation_method_values() -> None:
    """Test that AggregationMethod enum has the expected values."""
    assert AggregationMethod.AVG.value == "avg"
    assert AggregationMethod.MIN.value == "min"
    assert AggregationMethod.MAX.value == "max"


def test_aggregated_metric_value() -> None:
    """Test AggregatedMetricValue creation and string representation."""
    # Test with full data
    value = AggregatedMetricValue(
        avg=5.0,
        min=1.0,
        max=10.0,
        raw_values=[1.0, 5.0, 10.0],
    )
    assert value.avg == 5.0
    assert value.min == 1.0
    assert value.max == 10.0
    assert list(value.raw_values) == [1.0, 5.0, 10.0]
    assert str(value) == "avg:5.0<min:1.0 max:10.0 num_raw:3>"

    # Test with minimal data (only avg required)
    value = AggregatedMetricValue(
        avg=5.0,
        min=None,
        max=None,
        raw_values=[],
    )
    assert value.avg == 5.0
    assert value.min is None
    assert value.max is None
    assert not value.raw_values
    assert str(value) == "avg:5.0"
