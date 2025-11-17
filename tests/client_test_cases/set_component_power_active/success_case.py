# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful set_component_power_active call."""

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

# pylint: disable-next=import-error
from _config import RESPONSE_CLASS  # type: ignore[import-not-found]
from frequenz.client.base import conversion
from frequenz.client.common.microgrid.components import ComponentId

client_args = (ComponentId(1), 1000.0)
client_kwargs = {"request_lifetime": timedelta(minutes=9.0)}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once()
    request = stub_method.call_args[0][0]
    assert request.electrical_component_id == 1
    assert request.power == pytest.approx(1000.0)
    assert request.request_lifetime == pytest.approx(60.0 * 9.0)
    assert stub_method.call_args[1]["timeout"] == 60.0


expiry_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
grpc_response = RESPONSE_CLASS(valid_until_time=conversion.to_timestamp(expiry_time))


def assert_client_result(result: datetime) -> None:
    """Assert that the client result matches the expected expiry time."""
    assert result == expiry_time
    """Assert that the client result matches the expected expiry time."""
    assert result == expiry_time
