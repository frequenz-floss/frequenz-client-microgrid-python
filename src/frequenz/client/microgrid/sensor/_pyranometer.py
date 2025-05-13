# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""A pyranometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Pyranometer(Sensor):
    """A pyranometer sensor.

    Measures solar irradiance.
    """

    category: Literal[SensorCategory.PYRANOMETER] = SensorCategory.PYRANOMETER
    """The category of this sensor."""
