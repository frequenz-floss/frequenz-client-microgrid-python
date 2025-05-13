# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""All known sensor types."""

from typing import TypeAlias

from ._accelerometer import Accelerometer
from ._anemometer import Anemometer
from ._barometer import Barometer
from ._general_sensor import GeneralSensor
from ._hygrometer import Hygrometer
from ._problematic import (
    MismatchedCategorySensor,
    UnrecognizedSensor,
    UnspecifiedSensor,
)
from ._pyranometer import Pyranometer
from ._thermometer import Thermometer

ProblematicSensorTypes: TypeAlias = (
    UnrecognizedSensor | UnspecifiedSensor | MismatchedCategorySensor
)
"""All possible sensor types that have a problem."""

SensorTypes: TypeAlias = (
    Accelerometer
    | Anemometer
    | Barometer
    | GeneralSensor
    | Hygrometer
    | ProblematicSensorTypes
    | Pyranometer
    | Thermometer
)
"""All possible sensor types."""
