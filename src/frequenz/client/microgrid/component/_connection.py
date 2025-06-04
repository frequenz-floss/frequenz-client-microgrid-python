# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Component connection."""

import dataclasses
from datetime import datetime, timezone

from frequenz.client.common.microgrid.components import ComponentId

from .._lifetime import Lifetime


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComponentConnection:
    """A single electrical link between two components within a microgrid.

    A component connection represents the physical wiring as viewed from the grid
    connection point, if one exists, or from the islanding point, in case of an islanded
    microgrids.

    Note: Physical Representation
        This object is not about data flow but rather about the physical
        electrical connections between components. Therefore, the IDs for the
        source and destination components correspond to the actual setup within
        the microgrid.

    Note: Direction
        The direction of the connection follows the flow of current away from the
        grid connection point, or in case of islands, away from the islanding
        point. This direction is aligned with positive current according to the
        [Passive Sign Convention]
        (https://en.wikipedia.org/wiki/Passive_sign_convention).

    Note: Historical Data
        The timestamps of when a connection was created and terminated allow for
        tracking the changes over time to a microgrid, providing insights into
        when and how the microgrid infrastructure has been modified.
    """

    source: ComponentId
    """The unique identifier of the component where the connection originates.

    This is aligned with the direction of current flow away from the grid connection
    point, or in case of islands, away from the islanding point.
    """

    destination: ComponentId
    """The unique ID of the component where the connection terminates.

    This is the component towards which the current flows.
    """

    operational_lifetime: Lifetime = dataclasses.field(default_factory=Lifetime)
    """The operational lifetime of the connection."""

    def __post_init__(self) -> None:
        """Ensure that the source and destination components are different."""
        if self.source == self.destination:
            raise ValueError("Source and destination components must be different")

    def is_operational_at(self, timestamp: datetime) -> bool:
        """Check whether this connection is operational at a specific timestamp."""
        return self.operational_lifetime.is_operational_at(timestamp)

    def is_operational_now(self) -> bool:
        """Whether this connection is currently operational."""
        return self.is_operational_at(datetime.now(timezone.utc))

    def __str__(self) -> str:
        """Return a human-readable string representation of this instance."""
        return f"{self.source}->{self.destination}"
