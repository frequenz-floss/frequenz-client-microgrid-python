# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for empty sensor telemetry stream."""

from typing import Any, TypeAlias

import pytest
from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.sensor import SensorTelemetry

client_args = (SensorId(1), [metrics_pb2.Metric.METRIC_AC_CURRENT])

_Filter: TypeAlias = (
    microgrid_pb2.ReceiveSensorTelemetryStreamRequest.SensorTelemetryStreamFilter
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ReceiveSensorTelemetryStreamRequest(
            sensor_id=1,
            filter=_Filter(metrics=[metrics_pb2.Metric.METRIC_AC_CURRENT]),
        )
    )


# The mock response from the server
grpc_response = microgrid_pb2.ReceiveSensorTelemetryStreamResponse(
    telemetry=sensors_pb2.SensorTelemetry(
        sensor_id=1, metric_samples=[], state_snapshots=[]
    ),
)


# The expected result from the client method
async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client result matches the expected empty data."""
    result = await receiver.receive()
    assert result == SensorTelemetry(
        sensor_id=SensorId(1), metric_samples=[], state_snapshots=[]
    )

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
