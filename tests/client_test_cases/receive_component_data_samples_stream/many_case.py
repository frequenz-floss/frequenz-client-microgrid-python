# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful component data stream."""

from datetime import datetime, timezone
from typing import Any

import pytest
from frequenz.api.common.v1.metrics import metric_sample_pb2
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentDataSamples
from frequenz.client.microgrid.metrics import Metric, MetricSample
from frequenz.client.microgrid.metrics._sample import AggregatedMetricValue

client_args = (
    ComponentId(1),
    [
        metric_sample_pb2.Metric.METRIC_DC_VOLTAGE,
        metric_sample_pb2.Metric.METRIC_DC_CURRENT,
    ],
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ReceiveComponentDataStreamRequest(
            component_id=1,
            filter=microgrid_pb2.ReceiveComponentDataStreamRequest.ComponentDataStreamFilter(
                metrics=[
                    metric_sample_pb2.Metric.METRIC_DC_VOLTAGE,
                    metric_sample_pb2.Metric.METRIC_DC_CURRENT,
                ]
            ),
        ),
        timeout=60.0,
    )


timestamp = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
timestamp_proto = to_timestamp(timestamp)
grpc_response = [
    microgrid_pb2.ReceiveComponentDataStreamResponse(
        data=components_pb2.ComponentData(
            component_id=1,
            metric_samples=[
                metric_sample_pb2.MetricSample(
                    metric=metric_sample_pb2.Metric.METRIC_DC_VOLTAGE,
                    sampled_at=timestamp_proto,
                    value=metric_sample_pb2.MetricValueVariant(
                        simple_metric=metric_sample_pb2.SimpleMetricValue(value=230.5),
                    ),
                ),
                metric_sample_pb2.MetricSample(
                    metric=metric_sample_pb2.Metric.METRIC_DC_CURRENT,
                    sampled_at=timestamp_proto,
                    value=metric_sample_pb2.MetricValueVariant(
                        aggregated_metric=metric_sample_pb2.AggregatedMetricValue(
                            min_value=10.0,
                            max_value=10.5,
                            avg_value=10.2,
                            raw_values=[10.0, 10.1, 10.2, 10.3, 10.4, 10.5],
                        ),
                    ),
                ),
            ],
            states=[],
        ),
    ),
    microgrid_pb2.ReceiveComponentDataStreamResponse(
        data=components_pb2.ComponentData(
            component_id=1,
            metric_samples=[
                metric_sample_pb2.MetricSample(
                    metric=metric_sample_pb2.Metric.METRIC_DC_VOLTAGE,
                    sampled_at=timestamp_proto,
                    value=metric_sample_pb2.MetricValueVariant(
                        simple_metric=metric_sample_pb2.SimpleMetricValue(value=231.5),
                    ),
                ),
                metric_sample_pb2.MetricSample(
                    metric=metric_sample_pb2.Metric.METRIC_DC_CURRENT,
                    sampled_at=timestamp_proto,
                    value=metric_sample_pb2.MetricValueVariant(
                        aggregated_metric=metric_sample_pb2.AggregatedMetricValue(
                            min_value=12.0,
                            max_value=12.5,
                            avg_value=12.2,
                            raw_values=[12.0, 12.1, 12.2, 12.3, 12.4, 12.5],
                        ),
                    ),
                ),
            ],
            states=[],
        ),
    ),
]


async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client result matches the expected ComponentDataSamples."""
    result = await receiver.receive()
    assert result == ComponentDataSamples(
        component_id=ComponentId(1),
        metric_samples=[
            MetricSample(
                metric=Metric.DC_VOLTAGE,
                sampled_at=timestamp,
                value=pytest.approx(230.5),  # type: ignore[arg-type]
                bounds=[],
            ),
            MetricSample(
                metric=Metric.DC_CURRENT,
                sampled_at=timestamp,
                value=AggregatedMetricValue(
                    min=pytest.approx(10.0),  # type: ignore[arg-type]
                    max=pytest.approx(10.5),  # type: ignore[arg-type]
                    avg=pytest.approx(10.2),  # type: ignore[arg-type]
                    raw_values=pytest.approx(  # type: ignore[arg-type]
                        [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
                    ),
                ),
                bounds=[],
            ),
        ],
        states=[],
    )

    result = await receiver.receive()
    assert result == ComponentDataSamples(
        component_id=ComponentId(1),
        metric_samples=[
            MetricSample(
                metric=Metric.DC_VOLTAGE,
                sampled_at=timestamp,
                value=pytest.approx(231.5),  # type: ignore[arg-type]
                bounds=[],
            ),
            MetricSample(
                metric=Metric.DC_CURRENT,
                sampled_at=timestamp,
                value=AggregatedMetricValue(
                    min=pytest.approx(12.0),  # type: ignore[arg-type]
                    max=pytest.approx(12.5),  # type: ignore[arg-type]
                    avg=pytest.approx(12.2),  # type: ignore[arg-type]
                    raw_values=pytest.approx(  # type: ignore[arg-type]
                        [12.0, 12.1, 12.2, 12.3, 12.4, 12.5]
                    ),
                ),
                bounds=[],
            ),
        ],
        states=[],
    )

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
