# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Base sensor from which all other sensors inherit."""

import dataclasses
from datetime import datetime, timezone
from functools import cached_property
from typing import Any, Self

from .._id import SensorId
from .._lifetime import Lifetime
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class Sensor:
    """A base class for all sensors.

    A sensor measures a physical metric in the microgrid's surrounding
    environment.
    """

    id: SensorId
    """This sensor's ID."""

    category: SensorCategory | int
    """The category of this sensor.

    Note:
        This should not be used normally, you should test if a sensor
        [`isinstance`][] of a concrete sensor class instead.

        It is only provided for using with a newer version of the API where the
        client doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedSensor`][frequenz.client.microgrid.sensor.UnrecognizedSensor])
        and in case some low level code needs to know the category of a sensor.
    """

    name: str | None = None
    """The name of this sensor."""

    manufacturer: str | None = None
    """The manufacturer of this sensor."""

    model_name: str | None = None
    """The model name of this sensor."""

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of this sensor."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Sensor:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)

    def active_at(self, timestamp: datetime) -> bool:
        """Check whether this sensor is active at a specific timestamp."""
        return self.operational_lifetime.active_at(timestamp)

    @cached_property
    def active(self) -> bool:
        """Whether this sensor is currently active."""
        return self.active_at(datetime.now(timezone.utc))

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
        return f"{self.id}<{type(self).__name__}>{name}"
