# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for empty component data stream."""

from typing import Any

import pytest
from frequenz.api.common.v1.metrics import metric_sample_pb2
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentDataSamples

client_args = (ComponentId(1), [metric_sample_pb2.Metric.METRIC_AC_CURRENT])


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ReceiveComponentDataStreamRequest(
            component_id=1,
            filter=microgrid_pb2.ReceiveComponentDataStreamRequest.ComponentDataStreamFilter(
                metrics=[metric_sample_pb2.Metric.METRIC_AC_CURRENT]
            ),
        ),
        timeout=60.0,
    )


# The mock response from the server
grpc_response = microgrid_pb2.ReceiveComponentDataStreamResponse(
    data=components_pb2.ComponentData(component_id=1, metric_samples=[], states=[]),
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
