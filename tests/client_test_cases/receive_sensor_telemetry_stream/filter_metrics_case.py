# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for sensor telemetry stream with metric filtering."""

from datetime import datetime, timezone
from typing import Any, TypeAlias

import pytest
from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.metrics import Metric, MetricSample
from frequenz.client.microgrid.sensor import SensorTelemetry

client_args = (
    SensorId(1),
    [metrics_pb2.Metric.METRIC_AC_VOLTAGE],
)

_Filter: TypeAlias = (
    microgrid_pb2.ReceiveSensorTelemetryStreamRequest.SensorTelemetryStreamFilter
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ReceiveSensorTelemetryStreamRequest(
            sensor_id=1,
            filter=_Filter(metrics=[metrics_pb2.Metric.METRIC_AC_VOLTAGE]),
        )
    )


timestamp = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
timestamp_proto = to_timestamp(timestamp)
grpc_response = microgrid_pb2.ReceiveSensorTelemetryStreamResponse(
    telemetry=sensors_pb2.SensorTelemetry(
        sensor_id=1,
        metric_samples=[
            metrics_pb2.MetricSample(
                metric=metrics_pb2.Metric.METRIC_AC_VOLTAGE,
                sample_time=timestamp_proto,
                value=metrics_pb2.MetricValueVariant(
                    simple_metric=metrics_pb2.SimpleMetricValue(value=230.5),
                ),
            ),
        ],
    ),
)


async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client result contains only the filtered metric."""
    result = await receiver.receive()
    assert result == SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[
            MetricSample(
                metric=Metric.AC_VOLTAGE,
                sampled_at=timestamp,
                value=pytest.approx(230.5),  # type: ignore[arg-type]
                bounds=[],
            ),
        ],
        state_snapshots=[],
    )

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
