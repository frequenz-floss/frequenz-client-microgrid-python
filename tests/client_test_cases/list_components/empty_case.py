# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with no components."""

from typing import Any

from frequenz.api.microgrid.v1 import microgrid_pb2

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListComponentsRequest(component_ids=[], categories=[]),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListComponentsResponse(components=[])


def assert_client_result(result: Any) -> None:  # noqa: D103
    assert not list(result)
