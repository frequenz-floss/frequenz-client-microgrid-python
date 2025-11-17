# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of MetricSample and AggregatedMetricValue objects from protobuf messages."""

from collections.abc import Sequence

from frequenz.api.common.v1alpha8.metrics import bounds_pb2, metrics_pb2
from frequenz.client.base import conversion

from .._util import enum_from_proto
from ._bounds import Bounds
from ._bounds_proto import bounds_from_proto
from ._metric import Metric
from ._sample import AggregatedMetricValue, MetricSample


def aggregated_metric_sample_from_proto(
    message: metrics_pb2.AggregatedMetricValue,
) -> AggregatedMetricValue:
    """Convert a protobuf message to a `AggregatedMetricValue` object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting `AggregatedMetricValue` object.
    """
    return AggregatedMetricValue(
        avg=message.avg_value,
        min=message.min_value if message.HasField("min_value") else None,
        max=message.max_value if message.HasField("max_value") else None,
        raw_values=message.raw_values,
    )


def metric_sample_from_proto_with_issues(
    message: metrics_pb2.MetricSample,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> MetricSample:
    """Convert a protobuf message to a `MetricSample` object.

    Args:
        message: The protobuf message to convert.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting `MetricSample` object.
    """
    value: float | AggregatedMetricValue | None = None
    if message.HasField("value"):
        match message.value.WhichOneof("metric_value_variant"):
            case "simple_metric":
                value = message.value.simple_metric.value
            case "aggregated_metric":
                value = aggregated_metric_sample_from_proto(
                    message.value.aggregated_metric
                )

    metric = enum_from_proto(message.metric, Metric)

    return MetricSample(
        sampled_at=conversion.to_datetime(message.sample_time),
        metric=metric,
        value=value,
        bounds=_metric_bounds_from_proto(
            metric,
            message.bounds,
            major_issues=major_issues,
            minor_issues=minor_issues,
        ),
        # pylint: disable-next=fixme
        # TODO: Wrap the full connection object
        connection=(message.connection.name or None) if message.connection else None,
    )


def _metric_bounds_from_proto(
    metric: Metric | int,
    messages: Sequence[bounds_pb2.Bounds],
    *,
    major_issues: list[str],
    minor_issues: list[str],  # pylint:disable=unused-argument
) -> list[Bounds]:
    """Convert a sequence of bounds messages to a list of `Bounds`.

    Args:
        metric: The metric for which the bounds are defined, used for logging issues.
        messages: The sequence of bounds messages.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting list of `Bounds`.
    """
    bounds: list[Bounds] = []
    for pb_bound in messages:
        try:
            bound = bounds_from_proto(pb_bound)
        except ValueError as exc:
            metric_name = metric if isinstance(metric, int) else metric.name
            major_issues.append(
                f"bounds for {metric_name} is invalid ({exc}), ignoring these bounds"
            )
            continue
        bounds.append(bound)

    return bounds
