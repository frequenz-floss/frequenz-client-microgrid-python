# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Hygrometer sensor."""

from frequenz.client.microgrid import SensorId
from frequenz.client.microgrid.sensor import Hygrometer, SensorCategory


def test_init() -> None:
    """Test Hygrometer sensor initialization."""
    sensor_id = SensorId(1)
    sensor = Hygrometer(
        id=sensor_id,
        name="test_hygrometer",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert sensor.id == sensor_id
    assert sensor.name == "test_hygrometer"
    assert sensor.manufacturer == "test_manufacturer"
    assert sensor.model_name == "test_model"
    assert sensor.category == SensorCategory.HYGROMETER
