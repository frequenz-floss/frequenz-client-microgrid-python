# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sensor and sensor data classes."""

from datetime import datetime, timedelta, timezone

import pytest

from frequenz.client.microgrid import Lifetime, SensorId
from frequenz.client.microgrid.sensor import Sensor


@pytest.fixture
def now() -> datetime:
    """Get the current time."""
    return datetime.now(timezone.utc)


def test_sensor_creation_defaults() -> None:
    """Test Sensor defaults are as expected."""
    sensor = Sensor(id=SensorId(1))

    assert sensor.id == SensorId(1)
    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None
    assert sensor.operational_lifetime == Lifetime()


def test_sensor_creation_full(now: datetime) -> None:
    """Test Sensor creation with all fields."""
    start = now
    end = start + timedelta(days=1)
    sensor = Sensor(
        id=SensorId(1),
        name="test-sensor",
        manufacturer="Test Manufacturer",
        model_name="Test Model",
        operational_lifetime=Lifetime(
            start=start,
            end=end,
        ),
    )

    assert sensor.id == SensorId(1)
    assert sensor.name == "test-sensor"
    assert sensor.manufacturer == "Test Manufacturer"
    assert sensor.model_name == "Test Model"
    assert sensor.operational_lifetime.start == start
    assert sensor.operational_lifetime.end == end


@pytest.mark.parametrize(
    "name,expected_str",
    [(None, "<Sensor:SID1>"), ("test-sensor", "<Sensor:SID1:test-sensor>")],
    ids=["no-name", "with-name"],
)
def test_sensor_str(name: str | None, expected_str: str) -> None:
    """Test string representation of a sensor."""
    sensor = Sensor(
        id=SensorId(1),
        name=name,
        manufacturer="Test Manufacturer",
        model_name="Test Model",
        operational_lifetime=Lifetime(
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc) + timedelta(days=1),
        ),
    )
    assert str(sensor) == expected_str


_SENSOR = Sensor(
    id=SensorId(1),
    name="test",
    manufacturer="Test Mfg",
    model_name="Model A",
)

_DIFFERENT_NAME = Sensor(
    id=_SENSOR.id,
    name="different",
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)

_DIFFERENT_ID = Sensor(
    id=SensorId(2),
    name=_SENSOR.name,
    manufacturer=_SENSOR.manufacturer,
    model_name=_SENSOR.model_name,
)


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(_SENSOR, True, id="self"),
        pytest.param(_DIFFERENT_NAME, False, id="other-name"),
        pytest.param(_DIFFERENT_ID, False, id="other-id"),
    ],
    ids=lambda o: str(o.id) if isinstance(o, Sensor) else str(o),
)
def test_sensor_equality(comp: Sensor, expected: bool) -> None:
    """Test sensor equality."""
    assert (_SENSOR == comp) is expected
    assert (comp == _SENSOR) is expected
    assert (_SENSOR != comp) is not expected
    assert (comp != _SENSOR) is not expected


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(_SENSOR, True, id="self"),
        pytest.param(_DIFFERENT_NAME, True, id="other-name"),
        pytest.param(_DIFFERENT_ID, False, id="other-id"),
    ],
)
def test_sensor_identity(comp: Sensor, expected: bool) -> None:
    """Test sensor identity."""
    assert (_SENSOR.identity == comp.identity) is expected
    assert comp.identity == comp.id


_ALL_SENSORS_PARAMS = [
    pytest.param(_SENSOR, id="comp"),
    pytest.param(_DIFFERENT_NAME, id="name"),
    pytest.param(_DIFFERENT_ID, id="id"),
]


@pytest.mark.parametrize("comp1", _ALL_SENSORS_PARAMS)
@pytest.mark.parametrize("comp2", _ALL_SENSORS_PARAMS)
def test_sensor_hash(comp1: Sensor, comp2: Sensor) -> None:
    """Test that the Sensor hash is consistent."""
    # We can only say the hash are the same if the sensors are equal, if they
    # are not, they could still have the same hash (and they will if they have
    # only different non-hashable attributes)
    if comp1 == comp2:
        assert hash(comp1) == hash(comp2)
