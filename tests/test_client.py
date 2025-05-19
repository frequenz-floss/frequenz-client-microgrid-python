# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Tests for the MicrogridApiClient class."""


import pytest
from frequenz.api.microgrid.v1 import microgrid_pb2_grpc
from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions
from frequenz.client.base.retry import LinearBackoff

from frequenz.client.microgrid import (
    DEFAULT_CHANNEL_OPTIONS,
    ClientNotConnected,
    MicrogridApiClient,
)

from .util import patch_client_class

# pylint: disable=protected-access


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
