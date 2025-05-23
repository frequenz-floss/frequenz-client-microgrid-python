# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with category filtering."""

from typing import Any

from frequenz.api.common.v1.microgrid.components import (
    battery_pb2,
    components_pb2,
    inverter_pb2,
)
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    ComponentCategory,
    LiIonBattery,
    SolarInverter,
)

client_kwargs = {"categories": [ComponentCategory.BATTERY, ComponentCategory.INVERTER]}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListComponentsRequest(
            component_ids=[],
            categories=[
                components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
                components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            ],
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListComponentsResponse(
    components=[
        components_pb2.Component(
            id=2,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_SOLAR
                )
            ),
        ),
        components_pb2.Component(
            id=3,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                battery=battery_pb2.Battery(
                    type=battery_pb2.BatteryType.BATTERY_TYPE_LI_ION
                )
            ),
        ),
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected filtered components."""
    assert list(result) == [
        SolarInverter(id=ComponentId(2), microgrid_id=MicrogridId(0)),
        LiIonBattery(id=ComponentId(3), microgrid_id=MicrogridId(0)),
    ]
