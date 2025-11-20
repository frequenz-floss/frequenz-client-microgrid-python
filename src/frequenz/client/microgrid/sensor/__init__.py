# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Sensor types and utilities.

This module provides classes and utilities for working with sensors in a
microgrid environment. Sensors measure various physical metrics in the
surrounding environment, such as temperature, humidity, and solar irradiance.
"""

from ._sensor import Sensor
from ._state import (
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
)

__all__ = [
    "Sensor",
    "SensorDiagnostic",
    "SensorDiagnosticCode",
    "SensorStateCode",
    "SensorStateSnapshot",
]
