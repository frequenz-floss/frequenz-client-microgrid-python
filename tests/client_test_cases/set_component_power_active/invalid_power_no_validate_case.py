# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test case with invalid power and validate_arguments=False."""

import math
from datetime import timedelta
from typing import Any

# pylint: disable-next=import-error
from _config import RESPONSE_CLASS  # type: ignore[import-not-found]
from frequenz.client.common.microgrid.components import ComponentId

client_kwargs = {
    "component": ComponentId(1),
    "power": float("nan"),
    "request_lifetime": timedelta(seconds=60),
    "validate_arguments": False,
}


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    # We can't use float("nan") when comparing here because nan != nan
    # so instead of using assert_called_once_with, we use assert_called_once
    # and then check the arguments manually
    stub_method.assert_called_once()
    request = stub_method.call_args[0][0]
    assert request.electrical_component_id == 1
    assert math.isnan(request.power)
    assert request.request_lifetime == 60
    assert stub_method.call_args[1]["timeout"] == 60.0


grpc_response = RESPONSE_CLASS()


def assert_client_result(result: None) -> None:
    """Assert that the client result is None."""
    assert result is None
