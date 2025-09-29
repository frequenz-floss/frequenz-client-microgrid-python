# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sample class and related classes."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final

import pytest
from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid.metrics import (
    AggregatedMetricValue,
    AggregationMethod,
    Bounds,
    Metric,
    MetricSample,
)
from frequenz.client.microgrid.metrics._sample_proto import (
    aggregated_metric_sample_from_proto,
    metric_sample_from_proto_with_issues,
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


DATETIME: Final[datetime] = datetime(2023, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
TIMESTAMP: Final[Timestamp] = Timestamp(seconds=int(DATETIME.timestamp()))


@dataclass(frozen=True, kw_only=True)
class _MetricSampleConversionTestCase:
    """Test case for MetricSample protobuf conversion."""

    name: str
    """The description of the test case."""

    proto_message: metrics_pb2.MetricSample
    """The input protobuf message."""

    expected_sample: MetricSample
    """The expected MetricSample object."""

    expected_major_issues: list[str] = field(default_factory=list)
    """Expected major issues during conversion."""

    expected_minor_issues: list[str] = field(default_factory=list)
    """Expected minor issues during conversion."""


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


def test_aggregation_method_values() -> None:
    """Test that AggregationMethod enum has the expected values."""
    assert AggregationMethod.AVG.value == "avg"
    assert AggregationMethod.MIN.value == "min"
    assert AggregationMethod.MAX.value == "max"


@pytest.mark.parametrize(
    "avg, min_val, max_val, raw_values, expected_str",
    [
        pytest.param(
            5.0,
            1.0,
            10.0,
            [1.0, 5.0, 10.0],
            "avg:5.0<min:1.0 max:10.0 num_raw:3>",
            id="full_data",
        ),
        pytest.param(
            5.0,
            None,
            None,
            [],
            "avg:5.0",
            id="minimal_data",
        ),
    ],
)
def test_aggregated_metric_value(
    avg: float,
    min_val: float | None,
    max_val: float | None,
    raw_values: list[float],
    expected_str: str,
) -> None:
    """Test AggregatedMetricValue creation and string representation."""
    value = AggregatedMetricValue(
        avg=avg,
        min=min_val,
        max=max_val,
        raw_values=raw_values,
    )
    assert value.avg == avg
    assert value.min == min_val
    assert value.max == max_val
    assert list(value.raw_values) == raw_values
    assert str(value) == expected_str


@pytest.mark.parametrize(
    "value,connection",
    [
        pytest.param(
            5.0,
            None,
            id="simple_value",
        ),
        pytest.param(
            AggregatedMetricValue(
                avg=5.0,
                min=1.0,
                max=10.0,
                raw_values=[1.0, 5.0, 10.0],
            ),
            "dc_battery_0",
            id="aggregated_value",
        ),
        pytest.param(
            None,
            None,
            id="none_value",
        ),
    ],
)
def test_metric_sample_creation(
    now: datetime,
    value: float | AggregatedMetricValue | None,
    connection: str | None,
) -> None:
    """Test MetricSample creation with different value types."""
    bounds = [Bounds(lower=-10.0, upper=10.0)]
    sample = MetricSample(
        sampled_at=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=value,
        bounds=bounds,
        connection=connection,
    )
    assert sample.sampled_at == now
    assert sample.metric == Metric.AC_POWER_ACTIVE
    assert sample.value == value
    assert sample.bounds == bounds
    assert sample.connection == connection


@pytest.mark.parametrize(
    "value, method_results",
    [
        pytest.param(
            5.0,
            {
                AggregationMethod.AVG: 5.0,
                AggregationMethod.MIN: 5.0,
                AggregationMethod.MAX: 5.0,
            },
            id="simple_value",
        ),
        pytest.param(
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
            id="aggregated_value",
        ),
        pytest.param(
            None,
            {
                AggregationMethod.AVG: None,
                AggregationMethod.MIN: None,
                AggregationMethod.MAX: None,
            },
            id="none_value",
        ),
    ],
)
def test_metric_sample_as_single_value(
    now: datetime,
    value: float | AggregatedMetricValue | None,
    method_results: dict[AggregationMethod, float | None],
) -> None:
    """Test MetricSample.as_single_value with different value types and methods."""
    bounds = [Bounds(lower=-10.0, upper=10.0)]

    sample = MetricSample(
        sampled_at=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=value,
        bounds=bounds,
    )

    for method, expected in method_results.items():
        assert sample.as_single_value(aggregation_method=method) == expected


def test_metric_sample_multiple_bounds(now: datetime) -> None:
    """Test MetricSample creation with multiple bounds."""
    bounds = [
        Bounds(lower=-10.0, upper=-5.0),
        Bounds(lower=5.0, upper=10.0),
    ]
    sample = MetricSample(
        sampled_at=now,
        metric=Metric.AC_POWER_ACTIVE,
        value=7.0,
        bounds=bounds,
    )
    assert sample.bounds == bounds


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
    proto = metrics_pb2.AggregatedMetricValue(
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


@pytest.mark.parametrize(
    "case",
    [
        _MetricSampleConversionTestCase(
            name="simple_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds=[],
                connection=None,
            ),
        ),
        _MetricSampleConversionTestCase(
            name="aggregated_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
                value=metrics_pb2.MetricValueVariant(
                    aggregated_metric=metrics_pb2.AggregatedMetricValue(
                        avg_value=5.0, min_value=1.0, max_value=10.0
                    )
                ),
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=AggregatedMetricValue(avg=5.0, min=1.0, max=10.0, raw_values=[]),
                bounds=[],
                connection=None,
            ),
        ),
        _MetricSampleConversionTestCase(
            name="no_value",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=None,
                bounds=[],
                connection=None,
            ),
        ),
        _MetricSampleConversionTestCase(
            name="unrecognized_metric",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=999,  # type: ignore[arg-type]
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME, metric=999, value=5.0, bounds=[], connection=None
            ),
        ),
        _MetricSampleConversionTestCase(
            name="with_valid_bounds",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                bounds=[bounds_pb2.Bounds(lower=-10.0, upper=10.0)],
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds=[Bounds(lower=-10.0, upper=10.0)],
                connection=None,
            ),
        ),
        _MetricSampleConversionTestCase(
            name="with_invalid_bounds",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                bounds=[
                    bounds_pb2.Bounds(lower=-10.0, upper=10.0),
                    bounds_pb2.Bounds(lower=10.0, upper=-10.0),  # Invalid
                ],
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds=[Bounds(lower=-10.0, upper=10.0)],  # Invalid bounds are ignored
                connection=None,
            ),
            expected_major_issues=[
                (
                    "bounds for AC_POWER_ACTIVE is invalid (Lower bound (10.0) must be "
                    "less than or equal to upper bound (-10.0)), ignoring these bounds"
                )
            ],
        ),
        _MetricSampleConversionTestCase(
            name="with_source",
            proto_message=metrics_pb2.MetricSample(
                sample_time=TIMESTAMP,
                metric=Metric.AC_POWER_ACTIVE.value,
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=5.0)
                ),
                connection=metrics_pb2.MetricConnection(name="dc_battery_0"),
            ),
            expected_sample=MetricSample(
                sampled_at=DATETIME,
                metric=Metric.AC_POWER_ACTIVE,
                value=5.0,
                bounds=[],
                connection="dc_battery_0",
            ),
        ),
    ],
    ids=lambda case: case.name,
)
def test_metric_sample_from_proto_with_issues(
    case: _MetricSampleConversionTestCase,
) -> None:
    """Test conversion from protobuf message to MetricSample."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    # The timestamp in the expected sample needs to match the one from proto conversion
    # We use a fixed timestamp in test cases, so this is fine.
    # If dynamic timestamps were used, we'd need to adjust here or in the fixture.

    sample = metric_sample_from_proto_with_issues(
        case.proto_message,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert sample == case.expected_sample
    assert major_issues == case.expected_major_issues
    assert minor_issues == case.expected_minor_issues
