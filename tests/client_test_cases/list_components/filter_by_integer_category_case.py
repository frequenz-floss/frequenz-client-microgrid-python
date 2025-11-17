# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with integer category filtering."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import UnrecognizedComponent

client_kwargs = {"categories": [999]}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentsRequest(
            electrical_component_ids=[],
            electrical_component_categories=[999],  # type: ignore[list-item]
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListElectricalComponentsResponse(
    electrical_components=[
        electrical_components_pb2.ElectricalComponent(
            id=4,
            microgrid_id=1,
            category=999,  # type: ignore[arg-type]
        ),
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected filtered components."""
    assert list(result) == [
        UnrecognizedComponent(
            id=ComponentId(4), microgrid_id=MicrogridId(1), category=999
        )
    ]
