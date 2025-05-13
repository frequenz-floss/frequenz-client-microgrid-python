# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Accelerometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import Accelerometer, SensorCategory


def test_init() -> None:
    """Test Accelerometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Accelerometer(
        id=sensor_id,
        name="test_accelerometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_accelerometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.ACCELEROMETER
