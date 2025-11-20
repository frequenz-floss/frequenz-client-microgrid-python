# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sensor class."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.sensor import Sensor


def test_creation_with_defaults() -> None:
    """Test sensor creation with default values."""
    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
    )

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(2)
    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None
    assert sensor.operational_lifetime == Lifetime()


def test_creation_full() -> None:
    """Test sensor creation with all attributes."""
    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="temperature-sensor-1",
        manufacturer="Acme Corp",
        model_name="TempSense 3000",
    )

    assert sensor.id == SensorId(1)
    assert sensor.microgrid_id == MicrogridId(2)
    assert sensor.name == "temperature-sensor-1"
    assert sensor.manufacturer == "Acme Corp"
    assert sensor.model_name == "TempSense 3000"


@pytest.mark.parametrize(
    "name,expected_str",
    [
        (None, "<Sensor:SID1>"),
        ("temp-sensor", "<Sensor:SID1:temp-sensor>"),
    ],
    ids=["no-name", "with-name"],
)
def test_str(name: str | None, expected_str: str) -> None:
    """Test string representation of a sensor."""
    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name=name,
    )
    assert str(sensor) == expected_str


def test_identity() -> None:
    """Test sensor identity property."""
    sensor1 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
    )
    sensor2 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-b",  # Different name
    )
    sensor3 = Sensor(
        id=SensorId(2),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
    )

    # Same id and microgrid_id = same identity
    assert sensor1.identity == sensor2.identity
    assert sensor1.identity == (SensorId(1), MicrogridId(2))

    # Different id = different identity
    assert sensor1.identity != sensor3.identity


def test_equality() -> None:
    """Test sensor equality."""
    sensor1 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
        manufacturer="Mfg A",
    )
    sensor2 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
        manufacturer="Mfg A",
    )
    sensor3 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-b",  # Different name
        manufacturer="Mfg A",
    )

    # Same attributes = equal
    assert sensor1 == sensor2
    assert sensor2 == sensor1

    # Different attributes = not equal
    assert sensor1 != sensor3
    assert sensor3 != sensor1


def test_hash() -> None:
    """Test sensor hashing."""
    sensor1 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
    )
    sensor2 = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
    )
    sensor3 = Sensor(
        id=SensorId(2),
        microgrid_id=MicrogridId(2),
        name="sensor-a",
    )

    # Equal sensors have equal hashes
    assert hash(sensor1) == hash(sensor2)

    # Can be used in sets and dicts
    sensor_set = {sensor1, sensor2, sensor3}
    assert len(sensor_set) == 2  # sensor1 and sensor2 are the same


@pytest.mark.parametrize(
    "is_operational", [True, False], ids=["operational", "not-operational"]
)
def test_operational_at(is_operational: bool) -> None:
    """Test is_operational_at behavior."""
    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.is_operational_at.return_value = is_operational

    sensor = Sensor(
        id=SensorId(1),
        microgrid_id=MicrogridId(1),
        operational_lifetime=mock_lifetime,
    )

    test_time = datetime.now(timezone.utc)
    assert sensor.operational_lifetime.is_operational_at(test_time) == is_operational

    mock_lifetime.is_operational_at.assert_called_once_with(test_time)
