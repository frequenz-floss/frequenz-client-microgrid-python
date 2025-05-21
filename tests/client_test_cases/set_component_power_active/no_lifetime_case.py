# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test set_component_power_active with no lifetime: result should be None."""

from typing import Any

import pytest

# pylint: disable-next=import-error
from _config import RESPONSE_CLASS  # type: ignore[import-not-found]
from frequenz.client.common.microgrid.components import ComponentId

client_args = (ComponentId(1), 1000.0)


# No client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once()
    request = stub_method.call_args[0][0]
    assert request.component_id == 1
    assert request.power == pytest.approx(1000.0)
    assert stub_method.call_args[1]["timeout"] == 60.0


grpc_response = RESPONSE_CLASS()


def assert_client_result(result: Any) -> None:  # noqa: D103
    """Assert that the client result is None when no lifetime is provided."""
    assert result is None
    assert result is None
