# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for microgrid info retrieval with error."""

from typing import Any

from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode

from frequenz.client.microgrid import PermissionDenied
from tests.util import make_grpc_error

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(Empty(), timeout=60.0)


grpc_response = make_grpc_error(StatusCode.PERMISSION_DENIED)


def assert_client_exception(exception: Exception) -> None:
    """Assert that the client exception matches the expected error."""
    assert isinstance(exception, PermissionDenied)
    assert exception.grpc_error == grpc_response
