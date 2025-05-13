# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of SensorDataSamples objects from protobuf messages."""

from collections.abc import Set
from datetime import datetime

from frequenz.api.microgrid import common_pb2, microgrid_pb2, sensor_pb2
from frequenz.client.base import conversion

from .._id import SensorId
from .._util import enum_from_proto
from ._data import (
    SensorDataSamples,
    SensorErrorCode,
    SensorMetric,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)


def sensor_data_samples_from_proto(
    message: microgrid_pb2.ComponentData,
    metrics: Set[sensor_pb2.SensorMetric.ValueType],
) -> SensorDataSamples:
    """Convert a protobuf component data message to a sensor data object.

    Args:
        message: The protobuf message to convert.
        metrics: A set of metrics to filter the samples.

    Returns:
        The resulting `SensorDataSamples` object.
    """
    # At some point it might make sense to also log issues found in the samples, but
    # using a naive approach like in `component_from_proto` might spam the logs too
    # much, as we can receive several samples per second, and if a component is in
    # a unrecognized state for long, it will mean we will emit the same log message
    # again and again.
    ts = conversion.to_datetime(message.ts)
    return SensorDataSamples(
        sensor_id=SensorId(message.id),
        metrics=[
            sensor_metric_sample_from_proto(ts, sample)
            for sample in message.sensor.data.sensor_data
            if sample.sensor_metric in metrics
        ],
        states=[sensor_state_sample_from_proto(ts, message.sensor)],
    )


def sensor_metric_sample_from_proto(
    sampled_at: datetime, message: sensor_pb2.SensorData
) -> SensorMetricSample:
    """Convert a protobuf message to a `SensorMetricSample` object.

    Args:
        sampled_at: The time at which the sample was taken.
        message: The protobuf message to convert.

    Returns:
        The resulting `SensorMetricSample` object.
    """
    return SensorMetricSample(
        sampled_at=sampled_at,
        metric=enum_from_proto(message.sensor_metric, SensorMetric),
        value=message.value,
    )


def sensor_state_sample_from_proto(
    sampled_at: datetime, message: sensor_pb2.Sensor
) -> SensorStateSample:
    """Convert a protobuf message to a `SensorStateSample` object.

    Args:
        sampled_at: The time at which the sample was taken.
        message: The protobuf message to convert.

    Returns:
        The resulting `SensorStateSample` object.
    """
    # In v0.15 the enum has 3 values, UNSPECIFIED, OK, and ERROR. In v0.17
    # (common v0.6), it also have 3 values with the same tags, but OK is renamed
    # to ON, so this conversion should work fine for both versions.
    state = enum_from_proto(message.state.component_state, SensorStateCode)
    errors: set[SensorErrorCode | int] = set()
    warnings: set[SensorErrorCode | int] = set()
    for error in message.errors:
        match error.level:
            case common_pb2.ErrorLevel.ERROR_LEVEL_CRITICAL:
                errors.add(enum_from_proto(error.code, SensorErrorCode))
            case common_pb2.ErrorLevel.ERROR_LEVEL_WARN:
                warnings.add(enum_from_proto(error.code, SensorErrorCode))
            case _:
                # If we don´t know the level we treat it as an error just to be safe.
                errors.add(enum_from_proto(error.code, SensorErrorCode))

    return SensorStateSample(
        sampled_at=sampled_at,
        states=frozenset([state]),
        warnings=frozenset(warnings),
        errors=frozenset(errors),
    )
