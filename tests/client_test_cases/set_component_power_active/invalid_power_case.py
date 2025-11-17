# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test case with invalid power and validate_arguments=False."""

from datetime import timedelta
from unittest.mock import AsyncMock

# pylint: disable-next=import-error
from _config import RESPONSE_CLASS  # type: ignore[import-not-found]
from frequenz.client.common.microgrid.components import ComponentId

client_kwargs = {
    "component": ComponentId(1),
    "power": float("nan"),
    "request_lifetime": timedelta(seconds=60),
}


def assert_stub_method_call(stub_method: AsyncMock) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_not_called()


grpc_response = RESPONSE_CLASS()


def assert_client_exception(result: Exception) -> None:
    """Assert that the client raises a ValueError."""
    assert isinstance(result, ValueError)
    assert str(result) == "power cannot be NaN"
