# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""A thermometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Thermometer(Sensor):
    """A thermometer sensor.

    Measures temperature.
    """

    category: Literal[SensorCategory.THERMOMETER] = SensorCategory.THERMOMETER
    """The category of this sensor."""
