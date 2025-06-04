# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the ComponentDataSamples class and proto conversion."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest
from frequenz.api.common.v1.metrics import bounds_pb2, metric_sample_pb2
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid.component import (
    ComponentDataSamples,
    ComponentErrorCode,
    ComponentStateCode,
    ComponentStateSample,
)
from frequenz.client.microgrid.component._data_samples_proto import (
    component_data_samples_from_proto_with_issues,
)
from frequenz.client.microgrid.metrics import (
    AggregatedMetricValue,
    Bounds,
    Metric,
    MetricSample,
)

DATETIME = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
TIMESTAMP = Timestamp(seconds=int(DATETIME.timestamp()))


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def timestamp() -> datetime:
    """Provide a fixed timestamp for testing."""
    return DATETIME


@pytest.fixture
def metric_sample(timestamp: datetime) -> MetricSample:
    """Provide a test metric sample."""
    return MetricSample(
        metric=Metric.AC_ACTIVE_POWER,
        value=100.0,
        bounds=[],
        sampled_at=timestamp,
    )


@pytest.fixture
def state_sample(timestamp: datetime) -> ComponentStateSample:
    """Provide a test component state sample."""
    return ComponentStateSample(
        sampled_at=timestamp,
        states=frozenset([ComponentStateCode.READY]),
        warnings=frozenset(),
        errors=frozenset(),
    )


def test_init(
    component_id: ComponentId,
    metric_sample: MetricSample,
    state_sample: ComponentStateSample,
) -> None:
    """Test initialization of ComponentDataSamples."""
    data_samples = ComponentDataSamples(
        component_id=component_id,
        metric_samples=[metric_sample],
        states=[state_sample],
    )

    assert data_samples.component_id == component_id
    assert len(data_samples.metric_samples) == 1
    assert data_samples.metric_samples[0] == metric_sample
    assert len(data_samples.states) == 1
    assert data_samples.states[0] == state_sample


def test_equality(
    component_id: ComponentId,
    metric_sample: MetricSample,
    state_sample: ComponentStateSample,
) -> None:
    """Test equality of ComponentDataSamples instances."""
    data_samples1 = ComponentDataSamples(
        component_id=component_id,
        metric_samples=[metric_sample],
        states=[state_sample],
    )

    data_samples2 = ComponentDataSamples(
        component_id=component_id,
        metric_samples=[metric_sample],
        states=[state_sample],
    )

    different_id = ComponentDataSamples(
        component_id=ComponentId(99),
        metric_samples=[metric_sample],
        states=[state_sample],
    )

    different_metrics = ComponentDataSamples(
        component_id=component_id,
        metric_samples=[],
        states=[state_sample],
    )

    different_states = ComponentDataSamples(
        component_id=component_id,
        metric_samples=[metric_sample],
        states=[],
    )

    assert data_samples1 == data_samples2
    assert data_samples1 != different_id
    assert data_samples1 != different_metrics
    assert data_samples1 != different_states


@dataclass(frozen=True, kw_only=True)
class _ComponentDataSamplesConversionTestCase:
    """Test case for ComponentDataSamples protobuf conversion."""

    name: str
    """The description of the test case."""

    message: components_pb2.ComponentData
    """The input protobuf message."""

    expected_samples: ComponentDataSamples
    """The expected ComponentDataSamples object."""

    expected_major_issues: list[str] = field(default_factory=list)
    """Expected major issues during conversion."""

    expected_minor_issues: list[str] = field(default_factory=list)
    """Expected minor issues during conversion."""


@pytest.mark.parametrize(
    "case",
    [
        _ComponentDataSamplesConversionTestCase(
            name="empty",
            message=components_pb2.ComponentData(component_id=1),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(1), metric_samples=[], states=[]
            ),
        ),
        _ComponentDataSamplesConversionTestCase(
            name="metrics_only_valid",
            message=components_pb2.ComponentData(
                component_id=2,
                metric_samples=[
                    metric_sample_pb2.MetricSample(
                        sampled_at=TIMESTAMP,
                        metric=Metric.AC_ACTIVE_POWER.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=100.0
                            )
                        ),
                    )
                ],
            ),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(2),
                metric_samples=[
                    MetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.AC_ACTIVE_POWER,
                        value=100.0,
                        bounds=[],
                    )
                ],
                states=[],
            ),
        ),
        _ComponentDataSamplesConversionTestCase(
            name="states_only_valid",
            message=components_pb2.ComponentData(
                component_id=3,
                states=[
                    components_pb2.ComponentState(
                        sampled_at=TIMESTAMP,
                        states=[components_pb2.COMPONENT_STATE_CODE_READY],
                    )
                ],
            ),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(3),
                metric_samples=[],
                states=[
                    ComponentStateSample(
                        sampled_at=DATETIME,
                        states=frozenset([ComponentStateCode.READY]),
                        warnings=frozenset(),
                        errors=frozenset(),
                    )
                ],
            ),
        ),
        _ComponentDataSamplesConversionTestCase(
            name="metric_with_invalid_bounds",
            message=components_pb2.ComponentData(
                component_id=4,
                metric_samples=[
                    metric_sample_pb2.MetricSample(
                        sampled_at=TIMESTAMP,
                        metric=Metric.DC_CURRENT.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=50.0
                            )
                        ),
                        bounds=[bounds_pb2.Bounds(lower=10.0, upper=5.0)],  # Invalid
                    )
                ],
            ),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(4),
                metric_samples=[
                    MetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.DC_CURRENT,
                        value=50.0,
                        bounds=[],  # Invalid bounds are ignored
                    )
                ],
                states=[],
            ),
            expected_major_issues=[
                "bounds for DC_CURRENT is invalid (Lower bound (10.0) must be "
                "less than or equal to upper bound (5.0)), ignoring these bounds"
            ],
        ),
        _ComponentDataSamplesConversionTestCase(
            name="metric_with_valid_bounds_and_source",
            message=components_pb2.ComponentData(
                component_id=5,
                metric_samples=[
                    metric_sample_pb2.MetricSample(
                        sampled_at=TIMESTAMP,
                        metric=Metric.AC_FREQUENCY.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=50.0
                            )
                        ),
                        bounds=[bounds_pb2.Bounds(lower=49.0, upper=51.0)],
                        source="sensor_A",
                    )
                ],
            ),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(5),
                metric_samples=[
                    MetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.AC_FREQUENCY,
                        value=50.0,
                        bounds=[Bounds(lower=49.0, upper=51.0)],
                        connection="sensor_A",
                    )
                ],
                states=[],
            ),
        ),
        _ComponentDataSamplesConversionTestCase(
            name="full_example_with_issues",
            message=components_pb2.ComponentData(
                component_id=6,
                metric_samples=[
                    metric_sample_pb2.MetricSample(  # Simple metric
                        sampled_at=TIMESTAMP,
                        metric=Metric.AC_ACTIVE_POWER.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=150.0
                            )
                        ),
                    ),
                    metric_sample_pb2.MetricSample(  # Aggregated metric
                        sampled_at=TIMESTAMP,
                        metric=Metric.AC_REACTIVE_POWER.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            aggregated_metric=metric_sample_pb2.AggregatedMetricValue(
                                avg_value=75.0,
                                min_value=70.0,
                                max_value=80.0,
                                raw_values=[70.0, 75.0, 80.0],
                            )
                        ),
                    ),
                    metric_sample_pb2.MetricSample(  # Metric with invalid bounds
                        sampled_at=TIMESTAMP,
                        metric=Metric.AC_VOLTAGE.value,
                        value=metric_sample_pb2.MetricValueVariant(
                            simple_metric=metric_sample_pb2.SimpleMetricValue(
                                value=230.0
                            )
                        ),
                        bounds=[bounds_pb2.Bounds(lower=250.0, upper=220.0)],  # Invalid
                    ),
                ],
                states=[
                    components_pb2.ComponentState(
                        sampled_at=TIMESTAMP,
                        states=[components_pb2.COMPONENT_STATE_CODE_READY],
                        warnings=[
                            components_pb2.COMPONENT_ERROR_CODE_HARDWARE_INACCESSIBLE
                        ],
                        errors=[components_pb2.COMPONENT_ERROR_CODE_OVERCURRENT],
                    )
                ],
            ),
            expected_samples=ComponentDataSamples(
                component_id=ComponentId(6),
                metric_samples=[
                    MetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.AC_ACTIVE_POWER,
                        value=150.0,
                        bounds=[],
                    ),
                    MetricSample(
                        sampled_at=DATETIME,
                        metric=Metric.AC_REACTIVE_POWER,
                        value=AggregatedMetricValue(
                            avg=75.0, min=70.0, max=80.0, raw_values=[70.0, 75.0, 80.0]
                        ),
                        bounds=[],
                    ),
                    MetricSample(  # Metric with invalid bounds is parsed, bounds ignored
                        sampled_at=DATETIME,
                        metric=Metric.AC_VOLTAGE,
                        value=230.0,
                        bounds=[],
                    ),
                ],
                states=[
                    ComponentStateSample(
                        sampled_at=DATETIME,
                        states=frozenset([ComponentStateCode.READY]),
                        warnings=frozenset([ComponentErrorCode.HARDWARE_INACCESSIBLE]),
                        errors=frozenset([ComponentErrorCode.OVERCURRENT]),
                    )
                ],
            ),
            expected_major_issues=[
                "bounds for AC_VOLTAGE is invalid (Lower bound (250.0) must be less "
                "than or equal to upper bound (220.0)), ignoring these bounds"
            ],
        ),
    ],
    ids=lambda c: c.name,
)
def test_from_proto(
    case: _ComponentDataSamplesConversionTestCase,
) -> None:
    """Test conversion from proto message to ComponentDataSamples, checking issues."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    result = component_data_samples_from_proto_with_issues(
        case.message,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert result == case.expected_samples
    assert major_issues == case.expected_major_issues
    assert minor_issues == case.expected_minor_issues
