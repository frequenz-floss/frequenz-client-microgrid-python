# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Lifetime of a microgrid asset."""


from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cached_property


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

    def active_at(self, timestamp: datetime) -> bool:
        """Check whether this lifetime is active at a specific timestamp."""
        if self.start is not None and self.start > timestamp:
            return False
        if self.end is not None:
            return self.end >= timestamp
        # Both are None, so it is always active
        return True

    @cached_property
    def active(self) -> bool:
        """Whether this lifetime is currently active."""
        return self.active_at(datetime.now(timezone.utc))
