# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Barometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import Barometer, SensorCategory


def test_init() -> None:
    """Test Barometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Barometer(
        id=sensor_id,
        name="test_barometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_barometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.BAROMETER
