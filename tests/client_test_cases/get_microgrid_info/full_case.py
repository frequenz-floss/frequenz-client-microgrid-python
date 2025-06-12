# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful microgrid info retrieval."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest
from frequenz.api.common.v1 import location_pb2
from frequenz.api.common.v1.grid import delivery_area_pb2
from frequenz.api.common.v1.microgrid import microgrid_pb2 as microgrid_common_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId
from google.protobuf.empty_pb2 import Empty

from frequenz.client.microgrid import (
    DeliveryArea,
    EnergyMarketCodeType,
    Location,
    MicrogridInfo,
    MicrogridStatus,
)

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: AsyncMock) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(Empty(), timeout=60.0)


create_timestamp = datetime(2023, 1, 1, tzinfo=timezone.utc)
grpc_response = microgrid_pb2.GetMicrogridMetadataResponse(
    microgrid=microgrid_common_pb2.Microgrid(
        id=1234,
        enterprise_id=5678,
        name="Test Microgrid",
        delivery_area=delivery_area_pb2.DeliveryArea(
            code="Test Delivery Area",
            code_type=delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC,
        ),
        location=location_pb2.Location(
            latitude=37.7749, longitude=-122.4194, country_code="DE"
        ),
        status=microgrid_common_pb2.MICROGRID_STATUS_INACTIVE,
        create_timestamp=to_timestamp(create_timestamp),
    )
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected MicrogridInfo."""
    assert result == MicrogridInfo(
        id=MicrogridId(1234),
        enterprise_id=EnterpriseId(5678),
        name="Test Microgrid",
        delivery_area=DeliveryArea(
            code="Test Delivery Area", code_type=EnergyMarketCodeType.EUROPE_EIC
        ),
        location=Location(
            latitude=pytest.approx(37.7749),  # type: ignore[arg-type]
            longitude=pytest.approx(-122.4194),  # type: ignore[arg-type]
            country_code="DE",
        ),
        status=MicrogridStatus.INACTIVE,
        create_timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
    )
    assert not result.is_active
