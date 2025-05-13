# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of sensor objects."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import assert_never
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common import components_pb2
from frequenz.api.microgrid import microgrid_pb2, sensor_pb2

from frequenz.client.microgrid import ComponentCategory, Lifetime, SensorId
from frequenz.client.microgrid.sensor import Accelerometer, SensorCategory
from frequenz.client.microgrid.sensor._proto import (
    sensor_from_proto,
    sensor_from_proto_with_issues,
)

_BAD_COMPONENT_CATEGORY_PB = components_pb2.ComponentCategory.COMPONENT_CATEGORY_CHP
_BAD_COMPONENT_CATEGORY = ComponentCategory.CHP


@dataclass(frozen=True, kw_only=True)
class _SensorTestCase:  # pylint: disable=too-many-instance-attributes
    """Test case for sensor protobuf conversion."""

    test_id: str
    """Description of the test case."""

    has_name: bool = True
    """Whether to include name in the protobuf message."""

    has_manufacturer: bool = True
    """Whether to include manufacturer in the protobuf message."""

    has_model_name: bool = True
    """Whether to include model name in the protobuf message."""

    category: SensorCategory | int = SensorCategory.ACCELEROMETER
    """The sensor category to set."""

    has_mismatched_category: bool = False
    """Whether to include mismatched category in the protobuf message."""

    has_sensor_metadata: bool = True
    """Whether to include sensor metadata in the protobuf message."""

    expected_minor_issues: Sequence[str] = tuple()
    """Minor issues expected in the sensor."""

    expected_major_issues: Sequence[str] = tuple()
    """Major issues expected in the sensor."""


@pytest.fixture
def sensor_id() -> SensorId:
    """Provide a test sensor ID."""
    return SensorId(42)


# pylintt: disable=too-many-arguments,too-many-positional-arguments


@patch("frequenz.client.microgrid.sensor._proto.sensor_from_proto_with_issues")
def test_sensor_from_proto(
    mock_sensor_from_proto_with_issues: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test main sensor conversion from protobuf."""
    mock_proto = Mock(name="Sensor", spec=microgrid_pb2.Component)
    mock_sensor = Mock(name="Accelerometer", spec=Accelerometer)
    captured_major_issues: list[str] | None = None
    captured_minor_issues: list[str] | None = None

    def _fake_sensor_from_proto_with_issues(
        message: microgrid_pb2.Component,  # pylint: disable=unused-argument
        major_issues: list[str],
        minor_issues: list[str],
    ) -> Accelerometer:
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


@patch("frequenz.client.microgrid.sensor._proto.UnspecifiedSensor")
@patch("frequenz.client.microgrid.sensor._proto.UnrecognizedSensor")
@patch("frequenz.client.microgrid.sensor._proto.MismatchedCategorySensor")
@patch("frequenz.client.microgrid.sensor._proto.Accelerometer")
@patch("frequenz.client.microgrid.sensor._proto.Anemometer")
@patch("frequenz.client.microgrid.sensor._proto.Barometer")
@patch("frequenz.client.microgrid.sensor._proto.GeneralSensor")
@patch("frequenz.client.microgrid.sensor._proto.Hygrometer")
@patch("frequenz.client.microgrid.sensor._proto.Pyranometer")
@patch("frequenz.client.microgrid.sensor._proto.Thermometer")
@pytest.mark.parametrize(
    "case",
    [
        _SensorTestCase(
            test_id="complete",
        ),
        _SensorTestCase(
            test_id="missing_metadata",
            has_name=False,
            has_manufacturer=False,
            has_model_name=False,
            expected_minor_issues=[
                "name is empty",
                "manufacturer is empty",
                "model_name is empty",
            ],
        ),
        _SensorTestCase(
            test_id="unspecified_category",
            category=SensorCategory.UNSPECIFIED,
            expected_major_issues=["category is unspecified"],
        ),
        _SensorTestCase(
            test_id="unrecognized_category",
            category=999,
            expected_major_issues=["category is unrecognized"],
        ),
        _SensorTestCase(
            test_id="missing_sensor_metadata",
            category=SensorCategory.UNSPECIFIED,
            has_sensor_metadata=False,
            expected_major_issues=[
                "wrong sensor metadata (None)",
            ],
        ),
        _SensorTestCase(
            test_id="category_mismatch",
            category=SensorCategory.UNSPECIFIED,
            has_sensor_metadata=False,
            has_mismatched_category=True,
            expected_major_issues=[
                f"unexpected category for sensor ({_BAD_COMPONENT_CATEGORY_PB})",
                "wrong sensor metadata (None)",
            ],
        ),
        _SensorTestCase(
            test_id="accelerometer",
            category=SensorCategory.ACCELEROMETER,
        ),
        _SensorTestCase(
            test_id="anemometer",
            category=SensorCategory.ANEMOMETER,
        ),
        _SensorTestCase(
            test_id="barometer",
            category=SensorCategory.BAROMETER,
        ),
        _SensorTestCase(
            test_id="general_sensor",
            category=SensorCategory.GENERAL,
        ),
        _SensorTestCase(
            test_id="hygrometer",
            category=SensorCategory.HYGROMETER,
        ),
        _SensorTestCase(
            test_id="pyranometer",
            category=SensorCategory.PYRANOMETER,
        ),
        _SensorTestCase(
            test_id="thermometer",
            category=SensorCategory.THERMOMETER,
        ),
    ],
    ids=lambda case: case.test_id,
)
# pylint: disable-next=too-many-locals,too-many-arguments,too-many-positional-arguments
def test_component_from_proto_with_issues(
    mock_thermometer: Mock,
    mock_pyranometer: Mock,
    mock_hygrometer: Mock,
    mock_general_sensor: Mock,
    mock_barometer: Mock,
    mock_anemometer: Mock,
    mock_accelerometer: Mock,
    mock_mismatched_category: Mock,
    mock_unrecognized: Mock,
    mock_unspecified: Mock,
    case: _SensorTestCase,
    sensor_id: SensorId,
) -> None:
    """Test component conversion with metadata matching check."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    proto = microgrid_pb2.Component(
        id=int(sensor_id),
        category=(
            _BAD_COMPONENT_CATEGORY_PB
            if case.has_mismatched_category
            else components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
        ),
    )

    if case.has_name:
        proto.name = "test_component"
    if case.has_manufacturer:
        proto.manufacturer = "test_manufacturer"
    if case.has_model_name:
        proto.model_name = "test_model"
    if case.has_sensor_metadata:
        proto.sensor.CopyFrom(
            sensor_pb2.Metadata(
                type=(
                    case.category.value  # type: ignore[arg-type]
                    if isinstance(case.category, SensorCategory)
                    else case.category
                )
            )
        )

    _ = sensor_from_proto_with_issues(
        proto,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert major_issues == list(case.expected_major_issues)
    assert minor_issues == list(case.expected_minor_issues)

    if not case.has_sensor_metadata:
        if case.has_mismatched_category:
            mock_mismatched_category.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                category=case.category,
                component_category=_BAD_COMPONENT_CATEGORY,
                operational_lifetime=Lifetime(),
            )
            return
        mock_unspecified.assert_called_once_with(
            id=sensor_id,
            name=proto.name or None,
            manufacturer=proto.manufacturer or None,
            model_name=proto.model_name or None,
            operational_lifetime=Lifetime(),
        )

    match case.category:
        case SensorCategory.UNSPECIFIED:
            mock_unspecified.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.ACCELEROMETER:
            mock_accelerometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.ANEMOMETER:
            mock_anemometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.BAROMETER:
            mock_barometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.GENERAL:
            mock_general_sensor.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.HYGROMETER:
            mock_hygrometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.PYRANOMETER:
            mock_pyranometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.THERMOMETER:
            mock_thermometer.assert_called_once_with(
                id=sensor_id,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case int():
            mock_unrecognized.assert_called_once_with(
                id=sensor_id,
                category=case.category,
                name=proto.name or None,
                manufacturer=proto.manufacturer or None,
                model_name=proto.model_name or None,
                operational_lifetime=Lifetime(),
            )
        case unhandled:
            assert_never(unhandled)
