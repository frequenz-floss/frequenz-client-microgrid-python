# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH


"""Definitions for bounds."""

import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bounds:
    """A set of lower and upper bounds for any metric.

    The lower bound must be less than or equal to the upper bound.

    The units of the bounds are always the same as the related metric.
    """

    lower: float | None = None
    """The lower bound.

    If `None`, there is no lower bound.
    """

    upper: float | None = None
    """The upper bound.

    If `None`, there is no upper bound.
    """

    def __post_init__(self) -> None:
        """Validate these bounds."""
        if self.lower is None:
            return
        if self.upper is None:
            return
        if self.lower > self.upper:
            raise ValueError(
                f"Lower bound ({self.lower}) must be less than or equal to upper "
                f"bound ({self.upper})"
            )

    def __str__(self) -> str:
        """Return a string representation of these bounds."""
        return f"[{self.lower}, {self.upper}]"
