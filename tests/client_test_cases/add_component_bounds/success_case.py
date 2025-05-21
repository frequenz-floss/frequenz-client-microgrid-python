# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful component bounds addition."""

from datetime import datetime, timezone
from typing import Any

from frequenz.api.common.v1.metrics import bounds_pb2, metric_sample_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid import Validity
from frequenz.client.microgrid._client import DEFAULT_GRPC_CALL_TIMEOUT
from frequenz.client.microgrid.metrics import Bounds, Metric

client_args = (
    ComponentId(1),
    Metric.DC_VOLTAGE,
    [Bounds(lower=200.0, upper=250.0)],
)
client_kwargs = {
    "validity": Validity.FIFTEEN_MINUTES,
}

PbValidity = microgrid_pb2.ComponentBoundsValidityDuration

valid_until = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.AddComponentBoundsRequest(
            component_id=1,
            target_metric=metric_sample_pb2.Metric.METRIC_DC_VOLTAGE,
            bounds=[bounds_pb2.Bounds(lower=200.0, upper=250.0)],
            validity_duration=PbValidity.COMPONENT_BOUNDS_VALIDITY_DURATION_15_MINUTES,
        ),
        timeout=DEFAULT_GRPC_CALL_TIMEOUT,
    )


grpc_response = microgrid_pb2.AddComponentBoundsResponse(ts=to_timestamp(valid_until))


def assert_client_result(result: datetime) -> None:
    """Assert that the client result matches the expected valid_until datetime."""
    assert result == valid_until
