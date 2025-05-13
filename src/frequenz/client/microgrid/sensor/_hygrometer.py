# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""A hygrometer sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hygrometer(Sensor):
    """A hygrometer sensor.

    Measures humidity.
    """

    category: Literal[SensorCategory.HYGROMETER] = SensorCategory.HYGROMETER
    """The category of this sensor."""
