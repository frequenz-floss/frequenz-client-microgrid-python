# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition to work with metric sample values."""

import enum
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import assert_never

from ._bounds import Bounds
from ._metric import Metric


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


@dataclass(frozen=True, kw_only=True)
class MetricSample:
    """A sampled metric.

    This represents a single sample of a specific metric, the value of which is either
    measured at a particular time. The real-time system-defined bounds are optional and
    may not always be present or set.

    Note: Relationship Between Bounds and Metric Samples
        Suppose a metric sample for active power has a lower-bound of -10,000 W, and an
        upper-bound of 10,000 W. For the system to accept a charge command, clients need
        to request current values within the bounds.
    """

    sampled_at: datetime
    """The moment when the metric was sampled."""

    metric: Metric | int
    """The metric that was sampled."""

    # In the protocol this is float | AggregatedMetricValue, but for live data we can't
    # receive the AggregatedMetricValue, so we limit this to float for now.
    value: float | AggregatedMetricValue | None
    """The value of the sampled metric."""

    bounds: list[Bounds]
    """The bounds that apply to the metric sample.

    These bounds adapt in real-time to reflect the operating conditions at the time of
    aggregation or derivation.

    In the case of certain components like batteries, multiple bounds might exist. These
    multiple bounds collectively extend the range of allowable values, effectively
    forming a union of all given bounds. In such cases, the value of the metric must be
    within at least one of the bounds.

    In accordance with the passive sign convention, bounds that limit discharge would
    have negative numbers, while those limiting charge, such as for the State of Power
    (SoP) metric, would be positive. Hence bounds can have positive and negative values
    depending on the metric they represent.

    Example:
        The diagram below illustrates the relationship between the bounds.

        ```
             bound[0].lower                         bound[1].upper
        <-------|============|------------------|============|--------->
                     bound[0].upper      bound[1].lower

        ---- values here are disallowed and will be rejected
        ==== values here are allowed and will be accepted
        ```
    """

    connection: str | None = None
    """The electrical connection within the component from which the metric was sampled.

    This will be present when the same `Metric` can be obtained from multiple
    electrical connections within the component. Knowing the connection can help in
    certain control and monitoring applications.

    In cases where the component has just one connection for a metric, then the
    connection is `None`.

    Example:
        A hybrid inverter can have a DC string for a battery and another DC string for a
        PV array. The connection names could resemble, say, `dc_battery_0` and
        ``dc_pv_0`. A metric like DC voltage can be obtained from both connections. For
        an application to determine the SoC of the battery using the battery voltage,
        which connection the voltage metric was sampled from is important.
    """

    def as_single_value(
        self, *, aggregation_method: AggregationMethod = AggregationMethod.AVG
    ) -> float | None:
        """Return the value of this sample as a single value.

        if [`value`][frequenz.client.microgrid.metrics.MetricSample.value] is a `float`,
        it is returned as is. If `value` is an
        [`AggregatedMetricValue`][frequenz.client.microgrid.metrics.AggregatedMetricValue],
        the value is aggregated using the provided `aggregation_method`.

        Args:
            aggregation_method: The method to use to aggregate the value when `value` is
                a `AggregatedMetricValue`.

        Returns:
            The value of the sample as a single value, or `None` if the value is `None`.
        """
        match self.value:
            case float() | int():
                return self.value
            case AggregatedMetricValue():
                match aggregation_method:
                    case AggregationMethod.AVG:
                        return self.value.avg
                    case AggregationMethod.MIN:
                        return self.value.min
                    case AggregationMethod.MAX:
                        return self.value.max
                    case unexpected:
                        assert_never(unexpected)
            case None:
                return None
            case unexpected:
                assert_never(unexpected)
