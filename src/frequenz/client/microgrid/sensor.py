# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. [`Sensor`][frequenz.client.microgrid.sensor.Sensor]s
measure various physical metrics in the surrounding environment, such as temperature,
humidity, and solar irradiance.
"""

import dataclasses

from ._id import SensorId
from ._lifetime import Lifetime


@dataclasses.dataclass(frozen=True, kw_only=True)
class Sensor:
    """Measures environmental metrics in the microgrid."""

    id: SensorId
    """This sensor's ID."""

    name: str | None = None
    """The name of this sensor."""

    manufacturer: str | None = None
    """The manufacturer of this sensor."""

    model_name: str | None = None
    """The model name of this sensor."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this sensor."""

    @property
    def identity(self) -> SensorId:
        """The identity of this sensor.

        This uses the sensor ID to identify a sensor without considering the
        other attributes, so even if a sensor state changed, the identity
        remains the same.
        """
        return self.id

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        name = f":{self.name}" if self.name else ""
        return f"<{type(self).__name__}:{self.id}{name}>"
