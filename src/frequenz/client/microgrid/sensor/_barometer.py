# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""A barometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Barometer(Sensor):
    """A barometer sensor.

    Measures pressure.
    """

    category: Literal[SensorCategory.BAROMETER] = SensorCategory.BAROMETER
    """The category of this sensor."""
