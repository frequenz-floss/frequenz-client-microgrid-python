# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for GeneralSensor sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import GeneralSensor, SensorCategory


def test_init() -> None:
    """Test GeneralSensor sensor initialization."""
    sensor_id = SensorId(1)
    sensor = GeneralSensor(
        id=sensor_id,
        name="test_general_sensor",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_general_sensor"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.GENERAL
