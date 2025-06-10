# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of sensor and sensor data objects."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common import components_pb2
from frequenz.api.microgrid import common_pb2, microgrid_pb2, sensor_pb2
from frequenz.client.base import conversion
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid._sensor_proto import (
    sensor_data_samples_from_proto,
    sensor_from_proto,
    sensor_from_proto_with_issues,
    sensor_metric_sample_from_proto,
    sensor_state_sample_from_proto,
)
from frequenz.client.microgrid.sensor import (
    Sensor,
    SensorDataSamples,
    SensorErrorCode,
    SensorMetric,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)


@pytest.fixture
def now() -> datetime:
    """Return a fixed datetime object for testing."""
    return datetime.now(timezone.utc)


@pytest.fixture
def sensor_id() -> SensorId:
    """Provide a test sensor ID."""
    return SensorId(42)


@patch("frequenz.client.microgrid._sensor_proto.sensor_from_proto_with_issues")
def test_sensor_from_proto(
    mock_sensor_from_proto_with_issues: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test main sensor conversion from protobuf."""
    mock_proto = Mock(name="PbSensor", spec=microgrid_pb2.Component)
    mock_sensor = Mock(name="Sensor", spec=Sensor)
    captured_major_issues: list[str] | None = None
    captured_minor_issues: list[str] | None = None

    def _fake_sensor_from_proto_with_issues(
        _: microgrid_pb2.Component, major_issues: list[str], minor_issues: list[str]
    ) -> Sensor:
        """Fake function to simulate sensor conversion."""
        nonlocal captured_major_issues
        nonlocal captured_minor_issues
        captured_major_issues = major_issues
        captured_minor_issues = minor_issues

        major_issues.append("major issue")
        minor_issues.append("minor issue")
        return mock_sensor

    mock_sensor_from_proto_with_issues.side_effect = _fake_sensor_from_proto_with_issues

    with caplog.at_level("DEBUG"):
        sensor = sensor_from_proto(mock_proto)

    assert sensor is mock_sensor
    mock_sensor_from_proto_with_issues.assert_called_once_with(
        mock_proto,
        # We need to use the same instance here because it was mutated (it was called
        # with empty lists but they were mutated in the function)
        major_issues=captured_major_issues,
        minor_issues=captured_minor_issues,
    )
    assert captured_major_issues == ["major issue"]
    assert captured_minor_issues == ["minor issue"]
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "WARNING"
    assert "Found issues in sensor: major issue" in caplog.records[0].message
    assert caplog.records[1].levelname == "DEBUG"
    assert "Found minor issues in sensor: minor issue" in caplog.records[1].message


@dataclass(frozen=True, kw_only=True)
class _SensorTestCase:  # pylint: disable=too-many-instance-attributes
    """Test case for sensor protobuf conversion."""

    test_id: str
    """Description of the test case."""

    missing_optional_fields: bool = False
    """Whether to include name, manufacturer and model_name in the protobuf message."""

    missing_metadata: bool = False
    """Whether to include sensor metadata in the protobuf message."""

    has_wrong_category: bool = False
    """Whether to include sensor metadata in the protobuf message."""

    expected_minor_issues: Sequence[str] = tuple()
    """Minor issues expected in the sensor."""

    expected_major_issues: Sequence[str] = tuple()
    """Major issues expected in the sensor."""


@patch("frequenz.client.microgrid._sensor_proto.Sensor")
@pytest.mark.parametrize(
    "case",
    [
        _SensorTestCase(test_id="full"),
        _SensorTestCase(
            test_id="missing_metadata",
            missing_optional_fields=True,
            expected_minor_issues=[
                "name is empty",
                "manufacturer is empty",
                "model_name is empty",
            ],
        ),
        _SensorTestCase(
            test_id="wrong_category",
            has_wrong_category=True,
            expected_major_issues=[
                "unexpected category for sensor (10)",
            ],
        ),
        _SensorTestCase(
            test_id="missing_sensor_metadata",
            missing_metadata=True,
            # This is actually fine, we don't use the metadata
        ),
        _SensorTestCase(
            test_id="all_wrong",
            missing_metadata=True,
            has_wrong_category=True,
            missing_optional_fields=True,
            expected_major_issues=[
                "unexpected category for sensor (10)",
            ],
            expected_minor_issues=[
                "name is empty",
                "manufacturer is empty",
                "model_name is empty",
            ],
        ),
    ],
    ids=lambda case: case.test_id,
)
# pylint: disable-next=too-many-locals,too-many-arguments,too-many-positional-arguments
def test_sensor_from_proto_with_issues(
    mock_sensor: Mock, case: _SensorTestCase, sensor_id: SensorId
) -> None:
    """Test sensor conversion with metadata matching check."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    proto = microgrid_pb2.Component(
        id=int(sensor_id),
        category=(
            components_pb2.ComponentCategory.COMPONENT_CATEGORY_CHP
            if case.has_wrong_category
            else components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
    )

    if not case.missing_optional_fields:
        proto.name = "test_sensor"
        proto.manufacturer = "test_manufacturer"
        proto.model_name = "test_model"
    if not case.missing_metadata:
        proto.sensor.CopyFrom(
            sensor_pb2.Metadata(
                type=components_pb2.SensorType.SENSOR_TYPE_ACCELEROMETER
            )
        )

    _ = sensor_from_proto_with_issues(
        proto,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert major_issues == list(case.expected_major_issues)
    assert minor_issues == list(case.expected_minor_issues)

    mock_sensor.assert_called_once_with(
        id=sensor_id,
        name=proto.name or None,
        manufacturer=proto.manufacturer or None,
        model_name=proto.model_name or None,
        operational_lifetime=Lifetime(),
    )


@dataclass(frozen=True, kw_only=True)
class _SensorMetricSampleTestCase:
    """Test case for sensor_metric_sample_from_proto."""

    test_id: str
    proto_metric_value: sensor_pb2.SensorMetric.ValueType | int
    proto_value: float
    expected_metric: SensorMetric | int
    expected_value: float


@pytest.mark.parametrize(
    "case",
    [
        _SensorMetricSampleTestCase(
            test_id="valid_metric",
            proto_metric_value=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
            proto_value=25.5,
            expected_metric=SensorMetric.TEMPERATURE,
            expected_value=25.5,
        ),
        _SensorMetricSampleTestCase(
            test_id="unrecognized_metric",
            proto_metric_value=999,
            proto_value=10.0,
            expected_metric=999,
            expected_value=10.0,
        ),
    ],
    ids=lambda case: case.test_id,
)
def test_sensor_metric_sample_from_proto(
    case: _SensorMetricSampleTestCase, now: datetime
) -> None:
    """Test sensor_metric_sample_from_proto with different inputs."""
    proto_metric = sensor_pb2.SensorData(
        sensor_metric=case.proto_metric_value,  # type: ignore[arg-type]
        value=case.proto_value,
    )
    result = sensor_metric_sample_from_proto(now, proto_metric)

    assert isinstance(result, SensorMetricSample)
    assert result.sampled_at == now
    assert result.metric == case.expected_metric
    assert result.value == case.expected_value


@dataclass(frozen=True, kw_only=True)
class _SensorStateSampleTestCase:
    """Test case for sensor_state_sample_from_proto."""

    test_id: str
    proto_state_code: sensor_pb2.ComponentState.ValueType
    proto_errors: list[sensor_pb2.Error] = field(default_factory=list)
    expected_state_code: SensorStateCode | int
    expected_errors_set: frozenset[SensorErrorCode | int]
    expected_warnings_set: frozenset[SensorErrorCode | int]


@pytest.mark.parametrize(
    "case",
    [
        _SensorStateSampleTestCase(
            test_id="state_on_no_errors",
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_OK,
            expected_state_code=SensorStateCode.ON,
            expected_errors_set=frozenset(),
            expected_warnings_set=frozenset(),
        ),
        _SensorStateSampleTestCase(
            test_id="state_error_critical_error",
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_ERROR,
            proto_errors=[
                sensor_pb2.Error(
                    # Code only have UNSPECIFIED for now
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_CRITICAL,
                    msg="Critical error",
                )
            ],
            expected_state_code=SensorStateCode.ERROR,
            expected_errors_set=frozenset([SensorErrorCode.UNSPECIFIED]),
            expected_warnings_set=frozenset(),
        ),
        _SensorStateSampleTestCase(
            test_id="state_on_warning",
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_OK,
            proto_errors=[
                sensor_pb2.Error(
                    # We use some numeric unrecognized code for the warning
                    code=999,  # type: ignore[arg-type]
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_WARN,
                    msg="Warning",
                )
            ],
            expected_state_code=SensorStateCode.ON,
            expected_errors_set=frozenset(),
            expected_warnings_set=frozenset([999]),
        ),
        _SensorStateSampleTestCase(
            test_id="state_on_critical_and_warning",
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_OK,
            proto_errors=[
                sensor_pb2.Error(
                    code=999,  # type: ignore[arg-type]
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_CRITICAL,
                    msg="Critical error",
                ),
                sensor_pb2.Error(
                    code=666,  # type: ignore[arg-type]
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_WARN,
                    msg="Warning",
                ),
            ],
            expected_state_code=SensorStateCode.ON,
            expected_errors_set=frozenset([999]),
            expected_warnings_set=frozenset([666]),
        ),
        _SensorStateSampleTestCase(
            test_id="state_on_unspecified_level_error",
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_OK,
            proto_errors=[
                sensor_pb2.Error(
                    code=999,  # type: ignore[arg-type]
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_UNSPECIFIED,
                    msg="Unspecified error",
                )
            ],
            expected_state_code=SensorStateCode.ON,
            expected_errors_set=frozenset([999]),
            expected_warnings_set=frozenset(),
        ),
        _SensorStateSampleTestCase(
            test_id="unrecognized_state_code",
            proto_state_code=999,  # type: ignore[arg-type]
            expected_state_code=999,  # Expected to be the integer itself
            expected_errors_set=frozenset(),
            expected_warnings_set=frozenset(),
        ),
    ],
    ids=lambda case: case.test_id,
)
def test_sensor_state_sample_from_proto(
    case: _SensorStateSampleTestCase, now: datetime
) -> None:
    """Test conversion of state, errors, and warnings."""
    proto_sensor_comp_data = sensor_pb2.Sensor(
        state=sensor_pb2.State(component_state=case.proto_state_code),
        errors=case.proto_errors,
    )

    result = sensor_state_sample_from_proto(now, proto_sensor_comp_data)

    assert isinstance(result, SensorStateSample)
    assert result.sampled_at == now
    assert result.states == frozenset([case.expected_state_code])
    assert result.errors == case.expected_errors_set
    assert result.warnings == case.expected_warnings_set


@dataclass(frozen=True, kw_only=True)
class _SensorDataSamplesTestCase:  # pylint: disable=too-many-instance-attributes
    """Test case for sensor_data_samples_from_proto."""

    test_id: str
    proto_sensor_data: list[sensor_pb2.SensorData] = field(default_factory=list)
    filter_metrics_pb_values: set[sensor_pb2.SensorMetric.ValueType]
    expected_metrics_count: int
    expected_first_metric_details: tuple[SensorMetric, float] | None
    proto_state_code: sensor_pb2.ComponentState.ValueType = (
        sensor_pb2.ComponentState.COMPONENT_STATE_OK
    )
    proto_errors: list[sensor_pb2.Error] = field(default_factory=list)
    expected_state_code: SensorStateCode | int = SensorStateCode.ON
    expected_errors_set: frozenset[SensorErrorCode | int] = frozenset()
    expected_warnings_set: frozenset[SensorErrorCode | int] = frozenset()


@pytest.mark.parametrize(
    "case",
    [
        _SensorDataSamplesTestCase(
            test_id="one_metric_match_filter",
            proto_sensor_data=[
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                    value=20.0,
                )
            ],
            filter_metrics_pb_values={
                sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE
            },
            expected_metrics_count=1,
            expected_first_metric_details=(SensorMetric.TEMPERATURE, 20.0),
        ),
        _SensorDataSamplesTestCase(
            test_id="two_metrics_filter_one",
            proto_sensor_data=[
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                    value=20.0,
                ),
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_HUMIDITY,
                    value=60.0,
                ),
            ],
            filter_metrics_pb_values={
                sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE
            },
            expected_metrics_count=1,
            expected_first_metric_details=(SensorMetric.TEMPERATURE, 20.0),
        ),
        _SensorDataSamplesTestCase(
            test_id="two_metrics_filter_both",
            proto_sensor_data=[
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                    value=20.0,
                ),
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_HUMIDITY,
                    value=60.0,
                ),
            ],
            filter_metrics_pb_values={
                sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                sensor_pb2.SensorMetric.SENSOR_METRIC_HUMIDITY,
            },
            expected_metrics_count=2,
            expected_first_metric_details=(
                SensorMetric.TEMPERATURE,
                20.0,
            ),  # Checks first, assumes order
        ),
        _SensorDataSamplesTestCase(
            test_id="filter_none_empty_set",
            proto_sensor_data=[
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                    value=20.0,
                )
            ],
            filter_metrics_pb_values=set(),  # Empty filter set
            expected_metrics_count=0,
            expected_first_metric_details=None,
        ),
        _SensorDataSamplesTestCase(
            test_id="filter_none_other_metric",
            proto_sensor_data=[
                sensor_pb2.SensorData(
                    sensor_metric=sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE,
                    value=20.0,
                )
            ],
            filter_metrics_pb_values={
                sensor_pb2.SensorMetric.SENSOR_METRIC_HUMIDITY
            },  # Filter for other metric
            expected_metrics_count=0,
            expected_first_metric_details=None,
        ),
        _SensorDataSamplesTestCase(
            test_id="no_metrics_in_proto",
            filter_metrics_pb_values={
                sensor_pb2.SensorMetric.SENSOR_METRIC_TEMPERATURE
            },
            expected_metrics_count=0,
            expected_first_metric_details=None,
        ),
        _SensorDataSamplesTestCase(
            test_id="state_details_propagation",
            filter_metrics_pb_values=set(),
            expected_metrics_count=0,
            expected_first_metric_details=None,
            proto_state_code=sensor_pb2.ComponentState.COMPONENT_STATE_ERROR,
            proto_errors=[
                sensor_pb2.Error(
                    code=sensor_pb2.ErrorCode.ERROR_CODE_UNSPECIFIED,  # The only option for now
                    level=common_pb2.ErrorLevel.ERROR_LEVEL_CRITICAL,
                    msg="Error message",
                )
            ],
            expected_state_code=SensorStateCode.ERROR,
            expected_errors_set=frozenset([SensorErrorCode.UNSPECIFIED]),
        ),
    ],
    ids=lambda case: case.test_id,
)
def test_sensor_data_samples_from_proto(
    case: _SensorDataSamplesTestCase,
    now: datetime,
) -> None:
    """Test metric filtering and overall structure of SensorDataSamples."""
    sensor_id_val = 123
    proto_sensor_data = microgrid_pb2.ComponentData(
        id=sensor_id_val,
        ts=conversion.to_timestamp(now),
        sensor=sensor_pb2.Sensor(
            data=sensor_pb2.Data(sensor_data=case.proto_sensor_data),
            state=sensor_pb2.State(component_state=case.proto_state_code),
            errors=case.proto_errors,
        ),
    )

    result = sensor_data_samples_from_proto(
        proto_sensor_data, case.filter_metrics_pb_values
    )

    assert isinstance(result, SensorDataSamples)
    assert result.sensor_id == SensorId(sensor_id_val)
    assert len(result.metrics) == case.expected_metrics_count

    if case.expected_metrics_count > 0 and case.expected_first_metric_details:
        expected_sample = SensorMetricSample(
            sampled_at=now,
            metric=case.expected_first_metric_details[0],
            value=case.expected_first_metric_details[1],
        )
        # Basic check of the first metric, assumes order and content correctness
        # More comprehensive checks could iterate through all expected metrics.
        assert result.metrics[0] == expected_sample
        for metric_sample in result.metrics:
            assert metric_sample.sampled_at == now

    # Check state part
    assert len(result.states) == 1
    state_sample = result.states[0]
    assert isinstance(state_sample, SensorStateSample)
    assert state_sample.sampled_at == now
    assert state_sample.states == frozenset([case.expected_state_code])
    assert state_sample.errors == case.expected_errors_set
    assert state_sample.warnings == case.expected_warnings_set
