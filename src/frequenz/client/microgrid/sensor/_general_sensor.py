# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""A general sensor."""

import dataclasses
from typing import Literal

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneralSensor(Sensor):
    """A general sensor.

    A sensor that does not fall into any other specific category.
    """

    category: Literal[SensorCategory.GENERAL] = SensorCategory.GENERAL
    """The category of this sensor."""
