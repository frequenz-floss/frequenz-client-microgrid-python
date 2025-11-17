# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Inverter component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from ._category import ComponentCategory
from ._component import Component


@enum.unique
class InverterType(enum.Enum):
    """The known types of inverters."""

    UNSPECIFIED = electrical_components_pb2.INVERTER_TYPE_UNSPECIFIED
    """The type of the inverter is unspecified."""

    BATTERY = electrical_components_pb2.INVERTER_TYPE_BATTERY
    """The inverter is a battery inverter."""

    SOLAR = electrical_components_pb2.INVERTER_TYPE_PV
    """The inverter is a solar inverter."""

    HYBRID = electrical_components_pb2.INVERTER_TYPE_HYBRID
    """The inverter is a hybrid inverter."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inverter(Component):
    """An abstract inverter component."""

    category: Literal[ComponentCategory.INVERTER] = ComponentCategory.INVERTER
    """The category of this component.

    Note:
        This should not be used normally, you should test if a component
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent])
        and in case some low level code needs to know the category of a component.
    """

    type: InverterType | int
    """The type of this inverter.

    Note:
        This should not be used normally, you should test if a inverter
        [`isinstance`][] of a concrete inverter class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new inverter type yet (i.e. for use with
        [`UnrecognizedInverter`][frequenz.client.microgrid.component.UnrecognizedInverter]).
    """

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is Inverter:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedInverter(Inverter):
    """An inverter of an unspecified type."""

    type: Literal[InverterType.UNSPECIFIED] = InverterType.UNSPECIFIED
    """The type of this inverter.

    Note:
        This should not be used normally, you should test if a inverter
        [`isinstance`][] of a concrete inverter class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new inverter type yet (i.e. for use with
        [`UnrecognizedInverter`][frequenz.client.microgrid.component.UnrecognizedInverter]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class BatteryInverter(Inverter):
    """A battery inverter."""

    type: Literal[InverterType.BATTERY] = InverterType.BATTERY
    """The type of this inverter.

    Note:
        This should not be used normally, you should test if a inverter
        [`isinstance`][] of a concrete inverter class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new inverter type yet (i.e. for use with
        [`UnrecognizedInverter`][frequenz.client.microgrid.component.UnrecognizedInverter]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class SolarInverter(Inverter):
    """A solar inverter."""

    type: Literal[InverterType.SOLAR] = InverterType.SOLAR
    """The type of this inverter.

    Note:
        This should not be used normally, you should test if a inverter
        [`isinstance`][] of a concrete inverter class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new inverter type yet (i.e. for use with
        [`UnrecognizedInverter`][frequenz.client.microgrid.component.UnrecognizedInverter]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class HybridInverter(Inverter):
    """A hybrid inverter."""

    type: Literal[InverterType.HYBRID] = InverterType.HYBRID
    """The type of this inverter.

    Note:
        This should not be used normally, you should test if a inverter
        [`isinstance`][] of a concrete inverter class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new inverter type yet (i.e. for use with
        [`UnrecognizedInverter`][frequenz.client.microgrid.component.UnrecognizedInverter]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedInverter(Inverter):
    """An inverter component."""

    type: int
    """The unrecognized type of this inverter."""


InverterTypes: TypeAlias = (
    UnspecifiedInverter
    | BatteryInverter
    | SolarInverter
    | HybridInverter
    | UnrecognizedInverter
)
"""All possible inverter types."""
