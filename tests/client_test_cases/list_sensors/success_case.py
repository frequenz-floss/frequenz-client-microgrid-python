# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful sensor listing."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

client_args = ()

grpc_response = microgrid_pb2.ListSensorsResponse(
    sensors=[
        sensors_pb2.Sensor(
            id=1,
            microgrid_id=100,
            name="Temperature Sensor 1",
            manufacturer="Acme Corp",
            model_name="TMP-100",
        ),
        sensors_pb2.Sensor(
            id=2,
            microgrid_id=100,
            name="Humidity Sensor 1",
            manufacturer="Acme Corp",
            model_name="HUM-200",
        ),
    ]
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListSensorRequest(sensor_ids=[]),
        timeout=60.0,
    )


async def assert_client_result(result: Any) -> None:
    """Assert that the client result matches expected sensors."""
    sensors = list(result)
    assert len(sensors) == 2

    assert sensors[0].id == SensorId(1)
    assert sensors[0].microgrid_id == MicrogridId(100)
    assert sensors[0].name == "Temperature Sensor 1"
    assert sensors[0].manufacturer == "Acme Corp"
    assert sensors[0].model_name == "TMP-100"

    assert sensors[1].id == SensorId(2)
    assert sensors[1].microgrid_id == MicrogridId(100)
    assert sensors[1].name == "Humidity Sensor 1"
    assert sensors[1].manufacturer == "Acme Corp"
    assert sensors[1].model_name == "HUM-200"
