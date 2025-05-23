# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with component ID filtering."""

from typing import Any

from frequenz.api.common.v1.microgrid.components import (
    battery_pb2,
    components_pb2,
    grid_pb2,
)
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import GridConnectionPoint, LiIonBattery

client_kwargs = {"components": [ComponentId(1), ComponentId(3)]}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListComponentsRequest(component_ids=[1, 3], categories=[]),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListComponentsResponse(
    components=[
        components_pb2.Component(
            id=1,
            microgrid_id=1,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_GRID,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                grid=grid_pb2.GridConnectionPoint(rated_fuse_current=10_000)
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
        GridConnectionPoint(
            id=ComponentId(1), microgrid_id=MicrogridId(1), rated_fuse_current=10_000
        ),
        LiIonBattery(id=ComponentId(3), microgrid_id=MicrogridId(0)),
    ]
