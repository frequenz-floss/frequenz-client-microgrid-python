# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Anemometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import Anemometer, SensorCategory


def test_init() -> None:
    """Test Anemometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Anemometer(
        id=sensor_id,
        name="test_anemometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_anemometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.ANEMOMETER
