# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful microgrid info retrieval."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2 as microgrid_common_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId
from google.protobuf.empty_pb2 import Empty

from frequenz.client.microgrid import MicrogridInfo, MicrogridStatus

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: AsyncMock) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(Empty(), timeout=60.0)


create_timestamp = datetime(2023, 1, 1, tzinfo=timezone.utc)
grpc_response = microgrid_pb2.GetMicrogridResponse(
    microgrid=microgrid_common_pb2.Microgrid()
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected MicrogridInfo."""
    assert result == MicrogridInfo(
        id=MicrogridId(0),
        enterprise_id=EnterpriseId(0),
        name=None,
        status=MicrogridStatus.UNSPECIFIED,
        location=None,
        delivery_area=None,
        create_timestamp=datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc),
    )
    assert result.is_active
