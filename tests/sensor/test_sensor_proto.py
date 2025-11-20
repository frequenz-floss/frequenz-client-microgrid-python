# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for protobuf conversion of Sensor objects."""

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId
from google.protobuf.timestamp_pb2 import Timestamp

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.sensor._sensor_proto import (
    sensor_from_proto,
    sensor_from_proto_with_issues,
)


def test_sensor_from_proto_complete() -> None:
    """Test parsing of a complete sensor proto."""
    proto = sensors_pb2.Sensor(
        id=1,
        microgrid_id=2,
        name="temp-sensor-1",
        manufacturer="Acme Corp",
        model_name="TempSense 3000",
    )
    proto.operational_lifetime.start_timestamp.CopyFrom(
        Timestamp(seconds=1696118400)  # 2023-10-01T00:00:00Z
    )
    proto.operational_lifetime.end_timestamp.CopyFrom(
        Timestamp(seconds=1727740800)  # 2024-10-01T00:00:00Z
    )

    sensor = sensor_from_proto(proto)

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(2)
    assert sensor.name == "temp-sensor-1"
    assert sensor.manufacturer == "Acme Corp"
    assert sensor.model_name == "TempSense 3000"
    assert sensor.operational_lifetime != Lifetime()  # Non-default lifetime


def test_sensor_from_proto_minimal() -> None:
    """Test parsing of a minimal sensor proto with defaults."""
    proto = sensors_pb2.Sensor(
        id=1,
        microgrid_id=2,
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(2)
    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None
    assert sensor.operational_lifetime == Lifetime()

    assert not major_issues
    assert sorted(minor_issues) == sorted(
        [
            "name is empty",
            "manufacturer is empty",
            "model_name is empty",
        ]
    )


def test_sensor_from_proto_empty_strings() -> None:
    """Test parsing with empty strings for optional fields."""
    proto = sensors_pb2.Sensor(
        id=1,
        microgrid_id=2,
        name="",
        manufacturer="",
        model_name="",
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None

    assert not major_issues
    assert sorted(minor_issues) == sorted(
        [
            "name is empty",
            "manufacturer is empty",
            "model_name is empty",
        ]
    )


def test_sensor_from_proto_partial() -> None:
    """Test parsing with some optional fields set."""
    proto = sensors_pb2.Sensor(
        id=1,
        microgrid_id=2,
        name="sensor-1",
        # manufacturer not set
        model_name="Model X",
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert sensor.name == "sensor-1"
    assert sensor.manufacturer is None
    assert sensor.model_name == "Model X"

    assert not major_issues
    assert minor_issues == ["manufacturer is empty"]


def test_sensor_from_proto_with_lifetime() -> None:
    """Test parsing with operational lifetime set."""
    proto = sensors_pb2.Sensor(
        id=1,
        microgrid_id=2,
        name="sensor-1",
    )
    proto.operational_lifetime.start_timestamp.CopyFrom(
        Timestamp(seconds=1696118400)  # 2023-10-01T00:00:00Z
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert sensor.operational_lifetime != Lifetime()
    # Minor issues for manufacturer and model_name
    assert not major_issues
    assert "manufacturer is empty" in minor_issues
    assert "model_name is empty" in minor_issues
