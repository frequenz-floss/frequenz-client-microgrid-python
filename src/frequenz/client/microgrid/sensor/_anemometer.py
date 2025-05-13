# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""An anemometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Anemometer(Sensor):
    """An anemometer sensor.

    Measures wind velocity and direction.
    """

    category: Literal[SensorCategory.ANEMOMETER] = SensorCategory.ANEMOMETER
    """The category of this sensor."""
