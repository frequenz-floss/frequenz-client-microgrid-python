# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""An accelerometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Accelerometer(Sensor):
    """An accelerometer sensor.

    Measures acceleration.
    """

    category: Literal[SensorCategory.ACCELEROMETER] = SensorCategory.ACCELEROMETER
    """The category of this sensor."""
