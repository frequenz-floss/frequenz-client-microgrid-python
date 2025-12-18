# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. [`Sensor`][frequenz.client.microgrid.sensor.Sensor]s
measure various physical metrics in the surrounding environment, such as temperature,
humidity, and solar irradiance.

# Sensor Telemetry

This package also provides several data structures for handling sensor readings
and states:

* [`SensorTelemetry`][frequenz.client.microgrid.sensor.SensorTelemetry]:
    Represents a collection of measurements and states from a sensor at a specific
    point in time, including [metric
    samples][frequenz.client.microgrid.metrics.MetricSample] and [state
    snapshots][frequenz.client.microgrid.sensor.SensorStateSnapshot].
* [`SensorStateSnapshot`][frequenz.client.microgrid.sensor.SensorStateSnapshot]:
    Contains the sensor's state codes and any associated diagnostic information.
* [`SensorDiagnostic`][frequenz.client.microgrid.sensor.SensorDiagnostic]:
    Represents a diagnostic message from a sensor, including an error code and
    optional additional information.
* [`SensorDiagnosticCode`][frequenz.client.microgrid.sensor.SensorDiagnosticCode]:
    Defines error codes that a sensor can report.
* [`SensorStateCode`][frequenz.client.microgrid.sensor.SensorStateCode]:
    Defines codes representing the operational state of a sensor.
"""

from ._sensor import Sensor
from ._state import (
    SensorDiagnostic,
    SensorDiagnosticCode,
    SensorStateCode,
    SensorStateSnapshot,
)
from ._telemetry import SensorTelemetry

__all__ = [
    "Sensor",
    "SensorDiagnostic",
    "SensorDiagnosticCode",
    "SensorStateCode",
    "SensorStateSnapshot",
    "SensorTelemetry",
]
