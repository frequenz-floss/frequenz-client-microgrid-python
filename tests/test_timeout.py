# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the timeout handling in the client."""

import time
from typing import Any, Iterator
from unittest.mock import patch

import grpc.aio
import pytest

# pylint: disable=no-name-in-module
from frequenz.api.microgrid.microgrid_pb2 import (
    ComponentFilter,
    ComponentList,
    ConnectionFilter,
    ConnectionList,
    PowerLevelParam,
)
from google.protobuf.empty_pb2 import Empty

# pylint: enable=no-name-in-module
from pytest_mock import MockerFixture

from frequenz.client.microgrid import ApiClient

from .mock_api import MockGrpcServer, MockMicrogridServicer

# How much late a response to a gRPC call should be. It is used to trigger a timeout
# error and needs to be greater than `GRPC_CALL_TIMEOUT`.
GRPC_SERVER_DELAY: float = 0.3


@pytest.fixture(autouse=True)
def fake_grpc_call_timeout() -> Iterator[float]:
    """Patch the default gRPC call timeout."""
    # Timeout applied to all gRPC calls under test. It is expected after that the gRPC
    # calls will raise an AioRpcError with status code equal to DEADLINE_EXCEEDED.
    grpc_call_timeout: float = 0.1

    with patch(
        "frequenz.client.microgrid._client.DEFAULT_GRPC_CALL_TIMEOUT",
        grpc_call_timeout,
    ):
        yield grpc_call_timeout


async def test_components_timeout(mocker: MockerFixture) -> None:
    """Test if the components() method properly raises a timeeout AioRpcError."""
    servicer = MockMicrogridServicer()

    def mock_list_components(
        request: ComponentFilter, context: Any  # pylint: disable=unused-argument
    ) -> ComponentList:
        time.sleep(GRPC_SERVER_DELAY)
        return ComponentList(components=[])

    mocker.patch.object(servicer, "ListComponents", mock_list_components)
    server = MockGrpcServer(servicer, port=57809)
    await server.start()

    target = "[::]:57809"
    grpc_channel = grpc.aio.insecure_channel(target)
    client = ApiClient(grpc_channel=grpc_channel, target=target)

    with pytest.raises(grpc.aio.AioRpcError) as err_ctx:
        _ = await client.components()
    assert err_ctx.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
    assert await server.graceful_shutdown()


async def test_connections_timeout(mocker: MockerFixture) -> None:
    """Test if the connections() method properly raises a timeout AioRpcError."""
    servicer = MockMicrogridServicer()

    def mock_list_connections(
        request: ConnectionFilter, context: Any  # pylint: disable=unused-argument
    ) -> ConnectionList:
        time.sleep(GRPC_SERVER_DELAY)
        return ConnectionList(connections=[])

    mocker.patch.object(servicer, "ListConnections", mock_list_connections)
    server = MockGrpcServer(servicer, port=57809)
    await server.start()

    target = "[::]:57809"
    grpc_channel = grpc.aio.insecure_channel(target)
    client = ApiClient(grpc_channel=grpc_channel, target=target)

    with pytest.raises(grpc.aio.AioRpcError) as err_ctx:
        _ = await client.connections()
    assert err_ctx.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
    assert await server.graceful_shutdown()


async def test_set_power_timeout(mocker: MockerFixture) -> None:
    """Test if the set_power() method properly raises a timeout AioRpcError."""
    servicer = MockMicrogridServicer()

    def mock_set_power(
        request: PowerLevelParam, context: Any  # pylint: disable=unused-argument
    ) -> Empty:
        time.sleep(GRPC_SERVER_DELAY)
        return Empty()

    mocker.patch.object(servicer, "SetPowerActive", mock_set_power)
    server = MockGrpcServer(servicer, port=57809)
    await server.start()

    target = "[::]:57809"
    grpc_channel = grpc.aio.insecure_channel(target)
    client = ApiClient(grpc_channel=grpc_channel, target=target)

    power_values = [-100, 100]
    for power_w in power_values:
        with pytest.raises(grpc.aio.AioRpcError) as err_ctx:
            await client.set_power(component_id=1, power_w=power_w)
        assert err_ctx.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED

    assert await server.graceful_shutdown()
