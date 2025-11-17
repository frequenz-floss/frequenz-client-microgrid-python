# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Electric vehicle (EV) charger component."""

import dataclasses
import enum
from typing import Any, Literal, Self, TypeAlias

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)

from ._category import ComponentCategory
from ._component import Component


@enum.unique
class EvChargerType(enum.Enum):
    """The known types of electric vehicle (EV) chargers."""

    UNSPECIFIED = electrical_components_pb2.EV_CHARGER_TYPE_UNSPECIFIED
    """The type of the EV charger is unspecified."""

    AC = electrical_components_pb2.EV_CHARGER_TYPE_AC
    """The EV charging station supports AC charging only."""

    DC = electrical_components_pb2.EV_CHARGER_TYPE_DC
    """The EV charging station supports DC charging only."""

    HYBRID = electrical_components_pb2.EV_CHARGER_TYPE_HYBRID
    """The EV charging station supports both AC and DC."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class EvCharger(Component):
    """An abstract EV charger component."""

    category: Literal[ComponentCategory.EV_CHARGER] = ComponentCategory.EV_CHARGER
    """The category of this component.

    Note:
        This should not be used normally, you should test if a component
        [`isinstance`][] of a concrete EV charger class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about a new category yet (i.e. for use with
        [`UnrecognizedComponent`][frequenz.client.microgrid.component.UnrecognizedComponent])
        and in case some low level code needs to know the category of a component.
    """

    type: EvChargerType | int
    """The type of this EV charger.

    Note:
        This should not be used normally, you should test if a EV charger
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new EV charger type yet (i.e. for use with
        [`UnrecognizedEvCharger`][frequenz.client.microgrid.component.UnrecognizedEvCharger]).
    """

    # pylint: disable-next=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """Prevent instantiation of this class."""
        if cls is EvCharger:
            raise TypeError(f"Cannot instantiate {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEvCharger(EvCharger):
    """An EV charger of an unspecified type."""

    type: Literal[EvChargerType.UNSPECIFIED] = EvChargerType.UNSPECIFIED
    """The type of this EV charger.

    Note:
        This should not be used normally, you should test if a EV charger
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new EV charger type yet (i.e. for use with
        [`UnrecognizedEvCharger`][frequenz.client.microgrid.component.UnrecognizedEvCharger]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class AcEvCharger(EvCharger):
    """An EV charger that supports AC charging only."""

    type: Literal[EvChargerType.AC] = EvChargerType.AC
    """The type of this EV charger.

    Note:
        This should not be used normally, you should test if a EV charger
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new EV charger type yet (i.e. for use with
        [`UnrecognizedEvCharger`][frequenz.client.microgrid.component.UnrecognizedEvCharger]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class DcEvCharger(EvCharger):
    """An EV charger that supports DC charging only."""

    type: Literal[EvChargerType.DC] = EvChargerType.DC
    """The type of this EV charger.

    Note:
        This should not be used normally, you should test if a EV charger
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new EV charger type yet (i.e. for use with
        [`UnrecognizedEvCharger`][frequenz.client.microgrid.component.UnrecognizedEvCharger]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class HybridEvCharger(EvCharger):
    """An EV charger that supports both AC and DC charging."""

    type: Literal[EvChargerType.HYBRID] = EvChargerType.HYBRID
    """The type of this EV charger.

    Note:
        This should not be used normally, you should test if a EV charger
        [`isinstance`][] of a concrete component class instead.

        It is only provided for using with a newer version of the API where the client
        doesn't know about the new EV charger type yet (i.e. for use with
        [`UnrecognizedEvCharger`][frequenz.client.microgrid.component.UnrecognizedEvCharger]).
    """


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnrecognizedEvCharger(EvCharger):
    """An EV charger of an unrecognized type."""

    type: int
    """The unrecognized type of this EV charger."""


EvChargerTypes: TypeAlias = (
    UnspecifiedEvCharger
    | AcEvCharger
    | DcEvCharger
    | HybridEvCharger
    | UnrecognizedEvCharger
)
"""All possible EV charger types."""
