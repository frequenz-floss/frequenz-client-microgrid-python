# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of MetricSample and AggregatedMetricValue objects from protobuf messages."""

from frequenz.api.common.v1.metrics import metric_sample_pb2

from ._sample import AggregatedMetricValue


def aggregated_metric_sample_from_proto(
    message: metric_sample_pb2.AggregatedMetricValue,
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
