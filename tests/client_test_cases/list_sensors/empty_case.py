# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for empty sensor list."""

from typing import Any

from frequenz.api.microgrid.v1alpha18 import microgrid_pb2

client_args = ()

grpc_response = microgrid_pb2.ListSensorsResponse(sensors=[])


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListSensorRequest(sensor_ids=[]),
        timeout=60.0,
    )


async def assert_client_result(result: Any) -> None:
    """Assert that the client result is an empty list."""
    sensors = list(result)
    assert len(sensors) == 0
