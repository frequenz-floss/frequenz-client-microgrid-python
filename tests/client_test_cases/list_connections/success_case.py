# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful connection listing."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.common.v1alpha8.microgrid import lifetime_pb2
from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.component import ComponentConnection

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentConnectionsRequest(
            source_electrical_component_ids=[], destination_electrical_component_ids=[]
        ),
        timeout=60.0,
    )


lifetime_start = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
grpc_response = microgrid_pb2.ListElectricalComponentConnectionsResponse(
    electrical_component_connections=[
        electrical_components_pb2.ElectricalComponentConnection(
            source_electrical_component_id=1, destination_electrical_component_id=2
        ),
        electrical_components_pb2.ElectricalComponentConnection(
            source_electrical_component_id=2,
            destination_electrical_component_id=3,
            operational_lifetime=lifetime_pb2.Lifetime(
                start_timestamp=to_timestamp(lifetime_start)
            ),
        ),
    ]
)


def assert_client_result(actual_result: Any) -> None:
    """Assert that the client result matches the expected connections list."""
    assert list(actual_result) == [
        ComponentConnection(
            source=ComponentId(1),
            destination=ComponentId(2),
        ),
        ComponentConnection(
            source=ComponentId(2),
            destination=ComponentId(3),
            operational_lifetime=Lifetime(start=lifetime_start),
        ),
    ]
