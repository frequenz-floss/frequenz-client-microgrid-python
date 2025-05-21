# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the MicrogridApiClient class."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from frequenz.api.microgrid.v1 import microgrid_pb2_grpc
from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions
from frequenz.client.base.retry import LinearBackoff

from frequenz.client.microgrid import (
    DEFAULT_CHANNEL_OPTIONS,
    ClientNotConnected,
    MicrogridApiClient,
)

from .util import ApiClientTestCaseSpec, get_test_specs, patch_client_class

# pylint: disable=protected-access

TESTS_DIR = Path(__file__).parent / "client_test_cases"


@pytest.fixture
async def client() -> AsyncIterator[MicrogridApiClient]:
    """Fixture that provides a MicrogridApiClient with a mock gRPC stub and channel."""
    with patch_client_class(MicrogridApiClient, microgrid_pb2_grpc.MicrogridStub):
        client = MicrogridApiClient(
            "grpc://localhost:1234",
            # Retry very fast to avoid long test times, and also not too many
            # times to avoid test hanging forever.
            retry_strategy=LinearBackoff(interval=0.0, jitter=0.0, limit=10),
        )
        async with client:
            yield client


@patch_client_class(MicrogridApiClient, microgrid_pb2_grpc.MicrogridStub)
def test_init_defaults() -> None:
    """Test that MicrogridApiClient initializes correctly with defaults (connected)."""
    client = MicrogridApiClient("grpc://localhost:1234")
    assert client.server_url == "grpc://localhost:1234"
    assert client.is_connected is True
    assert client.stub is not None
    assert client.channel_defaults == DEFAULT_CHANNEL_OPTIONS
    assert client._retry_strategy is None  # pylint: disable=protected-access


@patch_client_class(MicrogridApiClient, microgrid_pb2_grpc.MicrogridStub)
def test_init_not_connected() -> None:
    """Test that MicrogridApiClient initializes correctly when not connected."""
    client = MicrogridApiClient("grpc://localhost:1234", connect=False)
    assert client.server_url == "grpc://localhost:1234"
    assert client.is_connected is False
    with pytest.raises(ClientNotConnected) as excinfo:
        _ = client.stub
    assert "client is not connected" in str(excinfo.value).lower()
    assert "grpc://localhost:1234" in str(excinfo.value)


@patch_client_class(MicrogridApiClient, microgrid_pb2_grpc.MicrogridStub)
def test_init_with_defaults() -> None:
    """Test that MicrogridApiClient initializes correctly with custom defaults."""
    options = ChannelOptions(
        ssl=SslOptions(enabled=False),
        port=1234,
        keep_alive=KeepAliveOptions(enabled=False),
    )
    assert options != DEFAULT_CHANNEL_OPTIONS
    client = MicrogridApiClient("grpc://localhost:1234", channel_defaults=options)
    assert client.channel_defaults == options


@patch_client_class(MicrogridApiClient, microgrid_pb2_grpc.MicrogridStub)
def test_init_with_custom_retry_strategy() -> None:
    """Test that MicrogridApiClient initializes correctly with custom retry strategy."""
    retry_strategy = LinearBackoff(interval=0.1, jitter=0.1, limit=5)
    client = MicrogridApiClient(
        "grpc://localhost:1234", retry_strategy=retry_strategy, connect=False
    )
    client._retry_strategy = retry_strategy  # pylint: disable=protected-access


@pytest.mark.parametrize(
    "spec",
    get_test_specs("get_microgrid_info", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_get_microgrid_info(
    client: MicrogridApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test get_microgrid_info method."""
    await spec.test_unary_unary_call(client, "GetMicrogridMetadata")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("set_component_power_active", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_set_component_power_active(
    client: MicrogridApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test set_component_power_active method."""
    await spec.test_unary_unary_call(client, "SetComponentPowerActive")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "spec",
    get_test_specs("set_component_power_reactive", tests_dir=TESTS_DIR),
    ids=str,
)
async def test_set_component_power_reactive(
    client: MicrogridApiClient, spec: ApiClientTestCaseSpec
) -> None:
    """Test set_component_power_reactive method."""
    await spec.test_unary_unary_call(client, "SetComponentPowerReactive")
