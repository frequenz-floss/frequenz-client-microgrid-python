# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for error case in sensor listing."""

from typing import Any

import grpc
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2

from tests.util import make_grpc_error

client_args = ()

grpc_response = make_grpc_error(grpc.StatusCode.INTERNAL)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListSensorRequest(sensor_ids=[]),
        timeout=60.0,
    )


def assert_client_exception(exception: Exception) -> None:
    """Assert that the client raised the expected exception."""
    from frequenz.client.microgrid import InternalError

    assert isinstance(exception, InternalError)
