# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Sensors that have a problem and can't be mapped to a known Sensor type."""

import dataclasses
from typing import Any, Literal, Self

from frequenz.client.microgrid._component import ComponentCategory

from ._base import Sensor
from ._category import SensorCategory


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProblematicSensor(Sensor):
    """An abstract sensor with a problem."""

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is ProblematicSensor:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedSensor(ProblematicSensor):
    """A sensor of unspecified type."""

    category: Literal[SensorCategory.UNSPECIFIED] = SensorCategory.UNSPECIFIED
    """The category of this sensor."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedSensor(ProblematicSensor):
    """A sensor of an unrecognized type."""

    category: int
    """The category of this sensor."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class MismatchedCategorySensor(ProblematicSensor):
    """A sensor with a mismatch in the category.

    This sensor has a component category different than COMPONENT_CATEGORY_SENSOR.
    doesn't match the declared category.
    """

    category: Literal[SensorCategory.UNSPECIFIED] = SensorCategory.UNSPECIFIED
    """The category of this sensor."""

    component_category: ComponentCategory | int
    """The actual category of this sensor."""
