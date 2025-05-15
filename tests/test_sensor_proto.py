# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of sensor and sensor data objects."""

from collections.abc import Sequence
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common import components_pb2
from frequenz.api.microgrid import microgrid_pb2, sensor_pb2

from frequenz.client.microgrid import Lifetime, SensorId
from frequenz.client.microgrid._sensor_proto import (
    sensor_from_proto,
    sensor_from_proto_with_issues,
)
from frequenz.client.microgrid.sensor import Sensor


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
