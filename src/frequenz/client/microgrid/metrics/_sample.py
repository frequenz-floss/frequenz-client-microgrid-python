# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition to work with metric sample values."""

import enum
from collections.abc import Sequence
from dataclasses import dataclass


@enum.unique
class AggregationMethod(enum.Enum):
    """The type of the aggregated value."""

    AVG = "avg"
    """The average value of the metric."""

    MIN = "min"
    """The minimum value of the metric."""

    MAX = "max"
    """The maximum value of the metric."""


@dataclass(frozen=True, kw_only=True)
class AggregatedMetricValue:
    """Encapsulates derived statistical summaries of a single metric.

    The message allows for the reporting of statistical summaries — minimum,
    maximum, and average values - as well as the complete list of individual
    samples if available.

    This message represents derived metrics and contains fields for statistical
    summaries—minimum, maximum, and average values. Individual measurements are
    are optional, accommodating scenarios where only subsets of this information
    are available.
    """

    avg: float
    """The derived average value of the metric."""

    min: float | None
    """The minimum measured value of the metric."""

    max: float | None
    """The maximum measured value of the metric."""

    raw_values: Sequence[float]
    """All the raw individual values (it might be empty if not provided by the component)."""

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        extra: list[str] = []
        if self.min is not None:
            extra.append(f"min:{self.min}")
        if self.max is not None:
            extra.append(f"max:{self.max}")
        if len(self.raw_values) > 0:
            extra.append(f"num_raw:{len(self.raw_values)}")
        extra_str = f"<{' '.join(extra)}>" if extra else ""
        return f"avg:{self.avg}{extra_str}"
