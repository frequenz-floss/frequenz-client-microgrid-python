# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for empty component data stream."""

from typing import Any, TypeAlias

import pytest
from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentDataSamples

client_args = (ComponentId(1), [metrics_pb2.Metric.METRIC_AC_CURRENT])

_Filter: TypeAlias = (
    microgrid_pb2.ReceiveElectricalComponentTelemetryStreamRequest.ComponentTelemetryStreamFilter
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ReceiveElectricalComponentTelemetryStreamRequest(
            electrical_component_id=1,
            filter=_Filter(metrics=[metrics_pb2.Metric.METRIC_AC_CURRENT]),
        )
    )


# The mock response from the server
grpc_response = microgrid_pb2.ReceiveElectricalComponentTelemetryStreamResponse(
    telemetry=electrical_components_pb2.ElectricalComponentTelemetry(
        electrical_component_id=1, metric_samples=[], state_snapshots=[]
    ),
)


# The expected result from the client method
async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client result matches the expected empty data."""
    result = await receiver.receive()
    assert result == ComponentDataSamples(
        component_id=ComponentId(1), metric_samples=[], states=[]
    )

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
