# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sample class and related classes."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from frequenz.client.microgrid.metrics import (
    AggregatedMetricValue,
    AggregationMethod,
)


@dataclass(frozen=True, kw_only=True)
class AggregatedValueTestCase:
    """Test case for AggregatedMetricValue protobuf conversion."""

    name: str
    """The description of the test case."""

    avg_value: float
    """The average value to set."""

    has_min: bool = True
    """Whether to include min value."""

    has_max: bool = True
    """Whether to include max value."""

    min_value: float | None = None
    """The minimum value to set."""

    max_value: float | None = None
    """The maximum value to set."""

    raw_values: list[float] = field(default_factory=list)
    """The raw values to include."""


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


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
