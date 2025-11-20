# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Sensor definition."""

from dataclasses import dataclass, field

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from .._lifetime import Lifetime


@dataclass(frozen=True, kw_only=True)
class Sensor:
    """A sensor that measures physical metrics in the microgrid's surroundings.

    Sensors are not part of the electrical infrastructure but provide
    environmental data such as temperature, humidity, and solar irradiance.
    """

    id: SensorId
    """A unique identifier for the sensor."""

    microgrid_id: MicrogridId
    """Unique identifier of the parent microgrid."""

    name: str | None = None
    """An optional name for the sensor."""

    manufacturer: str | None = None
    """The sensor manufacturer."""

    model_name: str | None = None
    """The model name of the sensor."""

    operational_lifetime: Lifetime = field(default_factory=Lifetime)
    """The operational lifetime of the sensor."""

    @property
    def identity(self) -> tuple[SensorId, MicrogridId]:
        """The identity of this sensor.

        This uses the sensor ID and microgrid ID to identify a sensor
        without considering the other attributes, so even if a sensor state
        changed, the identity remains the same.
        """
        return (self.id, self.microgrid_id)

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance.

        Returns:
            A string representation of this sensor.
        """
        name = f":{self.name}" if self.name else ""
        return f"<{type(self).__name__}:{self.id}{name}>"
