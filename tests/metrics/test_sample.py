# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sample class and related classes."""

from dataclasses import dataclass, field

import pytest
from frequenz.api.common.v1.metrics import metric_sample_pb2

from frequenz.client.microgrid.metrics import AggregatedMetricValue, AggregationMethod
from frequenz.client.microgrid.metrics._sample_proto import (
    aggregated_metric_sample_from_proto,
)


@dataclass(frozen=True, kw_only=True)
class _AggregatedValueTestCase:
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


@pytest.mark.parametrize(
    "case",
    [
        _AggregatedValueTestCase(
            name="full",
            avg_value=5.0,
            min_value=1.0,
            max_value=10.0,
            raw_values=[1.0, 5.0, 10.0],
        ),
        _AggregatedValueTestCase(
            name="minimal",
            avg_value=5.0,
            has_min=False,
            has_max=False,
        ),
        _AggregatedValueTestCase(
            name="only_min",
            avg_value=5.0,
            has_max=False,
            min_value=1.0,
        ),
        _AggregatedValueTestCase(
            name="only_max",
            avg_value=5.0,
            has_min=False,
            max_value=10.0,
        ),
    ],
    ids=lambda case: case.name,
)
def test_aggregated_metric_value_from_proto(case: _AggregatedValueTestCase) -> None:
    """Test conversion from protobuf message to AggregatedMetricValue."""
    proto = metric_sample_pb2.AggregatedMetricValue(
        avg_value=case.avg_value,
    )
    if case.has_min and case.min_value is not None:
        proto.min_value = case.min_value
    if case.has_max and case.max_value is not None:
        proto.max_value = case.max_value
    if case.raw_values:
        proto.raw_values.extend(case.raw_values)

    value = aggregated_metric_sample_from_proto(proto)

    assert value.avg == case.avg_value
    assert value.min == (case.min_value if case.has_min else None)
    assert value.max == (case.max_value if case.has_max else None)
    assert list(value.raw_values) == case.raw_values
