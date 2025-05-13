# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Sensor base class and its functionality."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from frequenz.client.microgrid import Lifetime, SensorId
from frequenz.client.microgrid.sensor._base import Sensor
from frequenz.client.microgrid.sensor._category import SensorCategory


# Test sensor subclass
class _FakeSensor(Sensor):
    """A simple sensor implementation for testing."""


def test_creation() -> None:
    """Test that Sensor base class cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Cannot instantiate Sensor directly"):
        _ = Sensor(
            id=SensorId(1),
            category=SensorCategory.UNSPECIFIED,
        )


@pytest.mark.parametrize(
    "name,expected_str",
    [(None, "SID1<_FakeSensor>"), ("test-sensor", "SID1<_FakeSensor>:test-sensor")],
    ids=["no-name", "with-name"],
)
def test_str(name: str | None, expected_str: str) -> None:
    """Test string representation of a sensor."""
    sensor = _FakeSensor(
        id=SensorId(1),
        category=SensorCategory.UNSPECIFIED,
        name=name,
    )
    assert str(sensor) == expected_str


def test_metadata() -> None:
    """Test sensor metadata fields."""
    sensor = _FakeSensor(
        id=SensorId(1),
        category=SensorCategory.UNSPECIFIED,
        name="test-sensor",
        manufacturer="Test Manufacturer",
        model_name="Test Model",
    )

    assert sensor.name == "test-sensor"
    assert sensor.manufacturer == "Test Manufacturer"
    assert sensor.model_name == "Test Model"


def test_default_values() -> None:
    """Test sensor default values."""
    sensor = _FakeSensor(
        id=SensorId(1),
        category=SensorCategory.UNSPECIFIED,
    )

    assert sensor.name is None
    assert sensor.manufacturer is None
    assert sensor.model_name is None
    assert sensor.operational_lifetime == Lifetime()


@pytest.mark.parametrize("lifetime_active", [True, False], ids=["active", "inactive"])
def test_active_at(lifetime_active: bool, caplog: pytest.LogCaptureFixture) -> None:
    """Test active_at behavior with different status and lifetime combinations."""
    caplog.set_level("WARNING")

    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.active_at.return_value = lifetime_active

    sensor = _FakeSensor(
        id=SensorId(1),
        category=SensorCategory.UNSPECIFIED,
        operational_lifetime=mock_lifetime,
    )

    test_time = datetime.now(timezone.utc)

    expected = lifetime_active
    assert sensor.active_at(test_time) == expected

    mock_lifetime.active_at.assert_called_once_with(test_time)


def test_active() -> None:
    """Test that active property uses active_at with current time."""
    fixed_now = datetime.now(timezone.utc)
    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.active_at.return_value = True

    with patch("frequenz.client.microgrid.sensor._base.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        sensor = _FakeSensor(
            id=SensorId(1),
            category=SensorCategory.UNSPECIFIED,
            operational_lifetime=mock_lifetime,
        )

        assert sensor.active is True

    mock_lifetime.active_at.assert_called_once_with(fixed_now)


SENSOR = _FakeSensor(
    id=SensorId(1),
    category=SensorCategory.UNSPECIFIED,
    name="test",
    manufacturer="Test Mfg",
    model_name="Model A",
)

DIFFERENT_NAME = _FakeSensor(
    id=SENSOR.id,
    category=SENSOR.category,
    name="different",
    manufacturer=SENSOR.manufacturer,
    model_name=SENSOR.model_name,
)

DIFFERENT_ID = _FakeSensor(
    id=SensorId(2),
    category=SENSOR.category,
    name=SENSOR.name,
    manufacturer=SENSOR.manufacturer,
    model_name=SENSOR.model_name,
)

DIFFERENT_BOTH_ID = _FakeSensor(
    id=SensorId(2),
    category=SENSOR.category,
    name=SENSOR.name,
    manufacturer=SENSOR.manufacturer,
    model_name=SENSOR.model_name,
)


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(SENSOR, True, id="self"),
        pytest.param(DIFFERENT_NAME, False, id="other-name"),
        pytest.param(DIFFERENT_ID, False, id="other-id"),
        pytest.param(DIFFERENT_BOTH_ID, False, id="other-both-ids"),
    ],
    ids=lambda o: str(o.id) if isinstance(o, Sensor) else str(o),
)
def test_equality(comp: Sensor, expected: bool) -> None:
    """Test sensor equality."""
    assert (SENSOR == comp) is expected
    assert (comp == SENSOR) is expected
    assert (SENSOR != comp) is not expected
    assert (comp != SENSOR) is not expected


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(SENSOR, True, id="self"),
        pytest.param(DIFFERENT_NAME, True, id="other-name"),
        pytest.param(DIFFERENT_ID, False, id="other-id"),
        pytest.param(DIFFERENT_BOTH_ID, False, id="other-both-ids"),
    ],
)
def test_identity(comp: Sensor, expected: bool) -> None:
    """Test sensor identity."""
    assert (SENSOR.identity == comp.identity) is expected
    assert comp.identity == comp.id


ALL_SENSORS_PARAMS = [
    pytest.param(SENSOR, id="comp"),
    pytest.param(DIFFERENT_NAME, id="name"),
    pytest.param(DIFFERENT_ID, id="id"),
    pytest.param(DIFFERENT_BOTH_ID, id="both_ids"),
]


@pytest.mark.parametrize("comp1", ALL_SENSORS_PARAMS)
@pytest.mark.parametrize("comp2", ALL_SENSORS_PARAMS)
def test_hash(comp1: Sensor, comp2: Sensor) -> None:
    """Test that the hash is consistent."""
    # We can only say the hash are the same if the sensors are equal, if they
    # are not, they could still have the same hash (and they will if they have
    # only different non-hashable attributes)
    if comp1 == comp2:
        assert hash(comp1) == hash(comp2)
