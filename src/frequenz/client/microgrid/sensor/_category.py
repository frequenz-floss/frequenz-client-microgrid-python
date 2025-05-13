# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""The component categories that can be used in a microgrid."""

import enum


@enum.unique
class SensorCategory(enum.Enum):
    """The known categories of sensors that can be present in a microgrid."""

    UNSPECIFIED = 0
    """Unspecified sensor category."""

    THERMOMETER = 1
    """Thermometer (temperature sensor)."""

    HYGROMETER = 2
    """Hygrometer (humidity sensor)."""

    BAROMETER = 3
    """Barometer (pressure sensor)."""

    PYRANOMETER = 4
    """Pyranometer (solar irradiance sensor)."""

    ANEMOMETER = 5
    """Anemometer (wind velocity and direction sensor)."""

    ACCELEROMETER = 6
    """Accelerometer (acceleration sensor)."""

    GENERAL = 7
    """General sensors, which do not fall in any of the above categories."""
