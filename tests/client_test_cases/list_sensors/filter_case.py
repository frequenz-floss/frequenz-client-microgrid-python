# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for filtered sensor listing."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.sensor import Sensor

# Filter by sensor IDs 1 and 3
client_kwargs = {
    "sensors": [
        SensorId(1),
        Sensor(id=SensorId(3), microgrid_id=MicrogridId(100)),
    ],
}

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
            id=3,
            microgrid_id=100,
            name="Pressure Sensor 1",
            manufacturer="Acme Corp",
            model_name="PRS-300",
        ),
    ]
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListSensorRequest(sensor_ids=[1, 3]),
        timeout=60.0,
    )


async def assert_client_result(result: Any) -> None:
    """Assert that the client result matches expected filtered sensors."""
    sensors = list(result)
    assert len(sensors) == 2

    assert sensors[0].id == SensorId(1)
    assert sensors[0].name == "Temperature Sensor 1"

    assert sensors[1].id == SensorId(3)
    assert sensors[1].name == "Pressure Sensor 1"
