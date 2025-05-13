# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sample class and related classes."""

from datetime import datetime, timezone
from typing import Any

import pytest

from frequenz.client.microgrid.metrics import (
    AggregatedMetricValue,
    AggregationMethod,
)
from frequenz.client.microgrid.sensor import SensorMetric, SensorMetricSample


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "metric,value",
    [
        (SensorMetric.TEMPERATURE, 5.0),
        (
            SensorMetric.HUMIDITY,
            AggregatedMetricValue(
                avg=5.0,
                min=1.0,
                max=10.0,
                raw_values=[1.0, 5.0, 10.0],
            ),
        ),
        (SensorMetric.DEW_POINT, None),
    ],
)
def test_metric_sample_creation(
    now: datetime, metric: SensorMetric, value: float | AggregatedMetricValue | None
) -> None:
    """Test MetricSample creation with different value types."""
    sample = SensorMetricSample(sampled_at=now, metric=metric, value=value)
    assert sample.sampled_at == now
    assert sample.metric == metric
    assert sample.value == value


@pytest.mark.parametrize(
    "value,method_results",
    [
        (
            5.0,
            {
                AggregationMethod.AVG: 5.0,
                AggregationMethod.MIN: 5.0,
                AggregationMethod.MAX: 5.0,
            },
        ),
        (
            AggregatedMetricValue(
                avg=5.0,
                min=1.0,
                max=10.0,
                raw_values=[1.0, 5.0, 10.0],
            ),
            {
                AggregationMethod.AVG: 5.0,
                AggregationMethod.MIN: 1.0,
                AggregationMethod.MAX: 10.0,
            },
        ),
        (
            None,
            {
                AggregationMethod.AVG: None,
                AggregationMethod.MIN: None,
                AggregationMethod.MAX: None,
            },
        ),
    ],
)
def test_metric_sample_as_single_value(
    now: datetime, value: Any, method_results: dict[AggregationMethod, float | None]
) -> None:
    """Test MetricSample.as_single_value with different value types and methods."""
    sample = SensorMetricSample(
        sampled_at=now, metric=SensorMetric.TEMPERATURE, value=value
    )

    for method, expected in method_results.items():
        assert sample.as_single_value(aggregation_method=method) == expected
