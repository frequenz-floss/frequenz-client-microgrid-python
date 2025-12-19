# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Proto conversion for sensor telemetry."""

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.client.common.microgrid.sensors import SensorId

from ..metrics._sample_proto import metric_sample_from_proto_with_issues
from ._state_proto import sensor_state_snapshot_from_proto
from ._telemetry import SensorTelemetry


def sensor_telemetry_from_proto(
    proto: sensors_pb2.SensorTelemetry,
) -> SensorTelemetry:
    """Convert a proto SensorTelemetry to a SensorTelemetry.

    Args:
        proto: The proto SensorTelemetry to convert.

    Returns:
        The converted SensorTelemetry.
    """
    # Convert metric samples
    # Using empty issue lists as we're not handling issues at this level
    # In a future improvement, we could expose issues to the caller
    major_issues: list[str] = []
    minor_issues: list[str] = []

    metric_samples = [
        metric_sample_from_proto_with_issues(
            sample,
            major_issues=major_issues,
            minor_issues=minor_issues,
        )
        for sample in proto.metric_samples
    ]

    # Convert state snapshots
    state_snapshots = [
        sensor_state_snapshot_from_proto(snapshot) for snapshot in proto.state_snapshots
    ]

    return SensorTelemetry(
        sensor_id=SensorId(proto.sensor_id),
        metric_samples=metric_samples,
        state_snapshots=state_snapshots,
    )
