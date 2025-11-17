# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with category filtering."""

from typing import Any, TypeAlias

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    ComponentCategory,
    LiIonBattery,
    SolarInverter,
)

client_kwargs = {"categories": [ComponentCategory.BATTERY, ComponentCategory.INVERTER]}

_CategorySpecificInfo: TypeAlias = (
    electrical_components_pb2.ElectricalComponentCategorySpecificInfo
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentsRequest(
            electrical_component_ids=[],
            electrical_component_categories=[
                electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
                electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            ],
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListElectricalComponentsResponse(
    electrical_components=[
        electrical_components_pb2.ElectricalComponent(
            id=2,
            category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=_CategorySpecificInfo(
                inverter=electrical_components_pb2.Inverter(
                    type=electrical_components_pb2.INVERTER_TYPE_PV
                )
            ),
        ),
        electrical_components_pb2.ElectricalComponent(
            id=3,
            category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=_CategorySpecificInfo(
                battery=electrical_components_pb2.Battery(
                    type=electrical_components_pb2.BATTERY_TYPE_LI_ION
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
