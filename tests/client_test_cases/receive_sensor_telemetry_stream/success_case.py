# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test data for successful sensor telemetry stream."""

from datetime import datetime, timezone
from typing import Any

import pytest
from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.api.common.v1alpha8.microgrid.sensors import sensors_pb2
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
from frequenz.channels import Receiver, ReceiverStoppedError
from frequenz.client.base.conversion import to_timestamp
from frequenz.client.common.microgrid.sensors import SensorId

from frequenz.client.microgrid.metrics import Metric, MetricSample
from frequenz.client.microgrid.metrics._sample import AggregatedMetricValue
from frequenz.client.microgrid.sensor import (
    SensorStateCode,
    SensorStateSnapshot,
    SensorTelemetry,
)

client_args = (
    SensorId(1),
    [
        metrics_pb2.Metric.METRIC_AC_VOLTAGE,
        metrics_pb2.Metric.METRIC_AC_CURRENT,
    ],
)


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once()
    called_args, called_kwargs = stub_method.call_args
    assert called_kwargs == {}
    assert len(called_args) == 1

    req = called_args[0]
    assert isinstance(req, microgrid_pb2.ReceiveSensorTelemetryStreamRequest)
    assert req.sensor_id == 1

    # The order of metrics in the filter is not guaranteed, so compare as a set.
    expected_metrics = {
        metrics_pb2.Metric.METRIC_AC_VOLTAGE,
        metrics_pb2.Metric.METRIC_AC_CURRENT,
    }
    assert set(req.filter.metrics) == expected_metrics


timestamp = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
timestamp_proto = to_timestamp(timestamp)
grpc_response = [
    microgrid_pb2.ReceiveSensorTelemetryStreamResponse(
        telemetry=sensors_pb2.SensorTelemetry(
            sensor_id=1,
            metric_samples=[
                metrics_pb2.MetricSample(
                    metric=metrics_pb2.Metric.METRIC_AC_VOLTAGE,
                    sample_time=timestamp_proto,
                    value=metrics_pb2.MetricValueVariant(
                        simple_metric=metrics_pb2.SimpleMetricValue(value=230.5),
                    ),
                ),
                metrics_pb2.MetricSample(
                    metric=metrics_pb2.Metric.METRIC_AC_CURRENT,
                    sample_time=timestamp_proto,
                    value=metrics_pb2.MetricValueVariant(
                        aggregated_metric=metrics_pb2.AggregatedMetricValue(
                            min_value=10.0,
                            max_value=10.5,
                            avg_value=10.2,
                            raw_values=[10.0, 10.1, 10.2, 10.3, 10.4, 10.5],
                        ),
                    ),
                ),
            ],
            state_snapshots=[
                sensors_pb2.SensorStateSnapshot(
                    origin_time=timestamp_proto,
                    states=[sensors_pb2.SENSOR_STATE_CODE_OK],
                )
            ],
        ),
    ),
    microgrid_pb2.ReceiveSensorTelemetryStreamResponse(
        telemetry=sensors_pb2.SensorTelemetry(
            sensor_id=1,
            metric_samples=[
                metrics_pb2.MetricSample(
                    metric=metrics_pb2.Metric.METRIC_AC_VOLTAGE,
                    sample_time=timestamp_proto,
                    value=metrics_pb2.MetricValueVariant(
                        simple_metric=metrics_pb2.SimpleMetricValue(value=231.5),
                    ),
                ),
                metrics_pb2.MetricSample(
                    metric=metrics_pb2.Metric.METRIC_AC_CURRENT,
                    sample_time=timestamp_proto,
                    value=metrics_pb2.MetricValueVariant(
                        aggregated_metric=metrics_pb2.AggregatedMetricValue(
                            min_value=12.0,
                            max_value=12.5,
                            avg_value=12.2,
                            raw_values=[12.0, 12.1, 12.2, 12.3, 12.4, 12.5],
                        ),
                    ),
                ),
            ],
            state_snapshots=[
                sensors_pb2.SensorStateSnapshot(
                    origin_time=timestamp_proto,
                    states=[sensors_pb2.SENSOR_STATE_CODE_OK],
                )
            ],
        ),
    ),
]


async def assert_client_result(receiver: Receiver[Any]) -> None:
    """Assert that the client result matches the expected SensorTelemetry."""
    result = await receiver.receive()
    assert result == SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[
            MetricSample(
                metric=Metric.AC_VOLTAGE,
                sampled_at=timestamp,
                value=pytest.approx(230.5),  # type: ignore[arg-type]
                bounds=[],
            ),
            MetricSample(
                metric=Metric.AC_CURRENT,
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
        state_snapshots=[
            SensorStateSnapshot(
                origin_time=timestamp,
                states={SensorStateCode.OK},
                warnings=[],
                errors=[],
            )
        ],
    )

    result = await receiver.receive()
    assert result == SensorTelemetry(
        sensor_id=SensorId(1),
        metric_samples=[
            MetricSample(
                metric=Metric.AC_VOLTAGE,
                sampled_at=timestamp,
                value=pytest.approx(231.5),  # type: ignore[arg-type]
                bounds=[],
            ),
            MetricSample(
                metric=Metric.AC_CURRENT,
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
        state_snapshots=[
            SensorStateSnapshot(
                origin_time=timestamp,
                states={SensorStateCode.OK},
                warnings=[],
                errors=[],
            )
        ],
    )

    with pytest.raises(ReceiverStoppedError):
        await receiver.receive()
