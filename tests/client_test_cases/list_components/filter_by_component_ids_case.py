# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with component ID filtering."""

from typing import Any, TypeAlias

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import GridConnectionPoint, LiIonBattery

client_kwargs = {"components": [ComponentId(1), ComponentId(3)]}


_CategorySpecificInfo: TypeAlias = (
    electrical_components_pb2.ElectricalComponentCategorySpecificInfo
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentsRequest(
            electrical_component_ids=[1, 3], electrical_component_categories=[]
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListElectricalComponentsResponse(
    electrical_components=[
        electrical_components_pb2.ElectricalComponent(
            id=1,
            microgrid_id=1,
            category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT,
            category_specific_info=_CategorySpecificInfo(
                grid_connection_point=electrical_components_pb2.GridConnectionPoint(
                    rated_fuse_current=10_000
                )
            ),
        ),
        electrical_components_pb2.ElectricalComponent(
            id=3,
            category=electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=_CategorySpecificInfo(
                battery=electrical_components_pb2.Battery(
                    type=electrical_components_pb2.BatteryType.BATTERY_TYPE_LI_ION
                )
            ),
        ),
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected filtered components."""
    assert list(result) == [
        GridConnectionPoint(
            id=ComponentId(1), microgrid_id=MicrogridId(1), rated_fuse_current=10_000
        ),
        LiIonBattery(id=ComponentId(3), microgrid_id=MicrogridId(0)),
    ]
