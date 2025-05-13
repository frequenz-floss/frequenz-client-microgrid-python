# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Pyranometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import Pyranometer, SensorCategory


def test_init() -> None:
    """Test Pyranometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Pyranometer(
        id=sensor_id,
        name="test_pyranometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_pyranometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.PYRANOMETER
