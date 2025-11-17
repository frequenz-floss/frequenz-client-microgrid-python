# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_connections with no connections: result should be empty."""

from typing import Any

from frequenz.api.microgrid.v1alpha18 import microgrid_pb2

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentConnectionsRequest(
            source_electrical_component_ids=[], destination_electrical_component_ids=[]
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListElectricalComponentConnectionsResponse(
    electrical_component_connections=[]
)


def assert_client_result(result: Any) -> None:  # noqa: D103
    """Assert that the client result is an empty list."""
    assert not list(result)
