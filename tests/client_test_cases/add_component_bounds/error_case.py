# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test add_component_bounds call with error."""

from typing import Any

from frequenz.client.common.microgrid.components import ComponentId
from grpc import StatusCode

from frequenz.client.microgrid import PermissionDenied
from frequenz.client.microgrid.metrics import Bounds, Metric
from tests.util import make_grpc_error

client_args = (ComponentId(1), Metric.AC_VOLTAGE, [Bounds(lower=200.0, upper=250.0)])


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    # We are not testing the request here, just the error handling


grpc_response = make_grpc_error(StatusCode.PERMISSION_DENIED)


def assert_client_exception(exception: Exception) -> None:
    """Assert that the client exception matches the expected error."""
    assert isinstance(exception, PermissionDenied)
    assert exception.grpc_error == grpc_response
