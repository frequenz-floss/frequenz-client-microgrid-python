# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Lifetime of a microgrid asset."""


from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, kw_only=True)
class Lifetime:
    """An active operational period of a microgrid asset.

    Warning:
        The [`end`][frequenz.client.microgrid.Lifetime.end] timestamp indicates that the
        asset has been permanently removed from the system.
    """

    start: datetime | None = None
    """The moment when the asset became operationally active.

    If `None`, the asset is considered to be active in any past moment previous to the
    [`end`][frequenz.client.microgrid.Lifetime.end].
    """

    end: datetime | None = None
    """The moment when the asset's operational activity ceased.

    If `None`, the asset is considered to be active with no plans to be deactivated.
    """

    def __post_init__(self) -> None:
        """Validate this lifetime."""
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("Start must be before or equal to end.")

    def is_operational_at(self, timestamp: datetime) -> bool:
        """Check whether this lifetime is active at a specific timestamp."""
        # Handle start time - it's not active if start is in the future
        if self.start is not None and self.start > timestamp:
            return False
        # Handle end time - active up to and including end time
        if self.end is not None:
            return self.end >= timestamp
        # self.end is None, and either self.start is None or self.start <= timestamp,
        # so it is active at this timestamp
        return True

    def is_operational_now(self) -> bool:
        """Whether this lifetime is currently active."""
        return self.is_operational_at(datetime.now(timezone.utc))
