# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for sensor telemetry stream with error."""

import enum
from collections.abc import AsyncIterator
from typing import Any, TypeAlias

import pytest
from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.common.microgrid.sensors import SensorId
from grpc import StatusCode

from frequenz.client.microgrid.sensor import SensorTelemetry
from tests.util import make_grpc_error

client_args = (SensorId(1), [metrics_pb2.Metric.METRIC_AC_VOLTAGE])

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


@enum.unique
class _State(enum.Enum):
    """State of the gRPC response simulation."""

    INITIAL = "initial"
    ERROR = "error"
    RECEIVING = "receiving"


_iterations: int = 0
_state: _State = _State.INITIAL


async def grpc_response() -> AsyncIterator[Any]:
    """Simulate a gRPC response with an error on the first iteration."""
    global _iterations, _state  # pylint: disable=global-statement

    _iterations += 1
    if _iterations == 1:
        _state = _State.ERROR
        raise make_grpc_error(StatusCode.UNAVAILABLE)

    _state = _State.RECEIVING
    for _ in range(3):
        yield microgrid_pb2.ReceiveSensorTelemetryStreamResponse(
            telemetry=sensors_pb2.SensorTelemetry(
                sensor_id=1, metric_samples=[], state_snapshots=[]
            ),
        )


# The expected result from the client method (exception in this case)
async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client can keep receiving data after an error."""
    assert _state is _State.ERROR

    async for result in receiver:
        assert result == SensorTelemetry(
            sensor_id=SensorId(1), metric_samples=[], state_snapshots=[]
        )
        # We need the type ignore here because mypy doesn't realize _state is
        # global and updated from outside this function, so it wrongly narrows
        # its type to `Literal[_State.ERROR]`, and complaining about the
        # impossibility of overlapping with _STATE.RECEIVING.
        # https://github.com/python/mypy/issues/19283
        assert _state is _State.RECEIVING  # type: ignore[comparison-overlap]

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
