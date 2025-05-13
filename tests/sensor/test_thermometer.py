# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Thermometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import SensorCategory, Thermometer


def test_init() -> None:
    """Test Thermometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Thermometer(
        id=sensor_id,
        name="test_thermometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_thermometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.THERMOMETER
