# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Grid connection point component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class GridConnectionPoint(Component):
    """A point where a microgrid connects to the grid.

    The terms "Grid Connection Point" and "Point of Common Coupling" (PCC) are
    commonly used in the context.

    While both terms describe a connection point to the grid, the
    `GridConnectionPoint` is specifically the physical connection point of the
    generation facility to the grid, often concerned with the technical and
    ownership aspects of the connection.

    In contrast, the PCC is is more specific in terms of electrical engineering.
    It refers to the point where a customer's local electrical system (such as a
    microgrid) connects to the utility distribution grid in such a way that it
    can affect other customers’ systems connected to the same network. It is the
    point where the grid and customer's electrical systems interface and where
    issues like power quality and supply regulations are assessed.

    The term `GridConnectionPoint` is used to make it clear that what is referred
    to here is the physical connection point of the local facility to the grid.
    Note that this may also be the PCC in some cases.
    """

    category: Literal[ComponentCategory.GRID_CONNECTION_POINT] = (
        ComponentCategory.GRID_CONNECTION_POINT
    )
    """The category of this component."""

    rated_fuse_current: int
    """The maximum amount of electrical current that can flow through this connection, in amperes.

    The rated maximum amount of current the fuse at the grid connection point is
    designed to safely carry under normal operating conditions.

    This limit applies to currents both flowing in or out of each of the 3
    phases individually.

    In other words, a current `i`A at one of the phases of the grid connection
    point must comply with the following constraint:
    `-rated_fuse_current <= i <= rated_fuse_current`
    """

    def __post_init__(self) -> None:
        """Validate the fuse's rated current."""
        if self.rated_fuse_current < 0:
            raise ValueError(
                f"rated_fuse_current must be a positive integer, not {self.rated_fuse_current}"
            )
