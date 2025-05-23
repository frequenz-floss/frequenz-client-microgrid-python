# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with integer category filtering."""

from typing import Any

from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import UnrecognizedComponent

client_kwargs = {"categories": [999]}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListComponentsRequest(
            component_ids=[],
            categories=[999],  # type: ignore[list-item]
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListComponentsResponse(
    components=[
        components_pb2.Component(
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
