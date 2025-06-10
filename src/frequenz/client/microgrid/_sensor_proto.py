# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of SensorDataSamples objects from protobuf messages."""

import logging
from collections.abc import Set
from datetime import datetime

from frequenz.api.common import components_pb2
from frequenz.api.microgrid import common_pb2, microgrid_pb2, sensor_pb2
from frequenz.client.base import conversion
from frequenz.client.common.microgrid.sensors import SensorId

from ._lifetime import Lifetime
from ._util import enum_from_proto
from .sensor import (
    Sensor,
    SensorDataSamples,
    SensorErrorCode,
    SensorMetric,
    SensorMetricSample,
    SensorStateCode,
    SensorStateSample,
)

_logger = logging.getLogger(__name__)


def sensor_from_proto(message: microgrid_pb2.Component) -> Sensor:
    """Convert a protobuf message to a `Sensor` instance.

    Args:
        message: The protobuf message.

    Returns:
        The resulting sensor instance.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    sensor = sensor_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in sensor: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in sensor: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return sensor


def sensor_from_proto_with_issues(
    message: microgrid_pb2.Component,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Sensor:
    """Convert a protobuf message to a sensor instance and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting sensor instance.
    """
    sensor_id = SensorId(message.id)

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    manufacturer = message.manufacturer or None
    if manufacturer is None:
        minor_issues.append("manufacturer is empty")

    model_name = message.model_name or None
    if model_name is None:
        minor_issues.append("model_name is empty")

    if (
        message.category
        is not components_pb2.ComponentCategory.COMPONENT_CATEGORY_SENSOR
    ):
        major_issues.append(f"unexpected category for sensor ({message.category})")

    return Sensor(
        id=sensor_id,
        name=name,
        manufacturer=manufacturer,
        model_name=model_name,
        operational_lifetime=Lifetime(),
    )


def sensor_data_samples_from_proto(
    message: microgrid_pb2.ComponentData,
    metrics: Set[sensor_pb2.SensorMetric.ValueType] | None = None,
) -> SensorDataSamples:
    """Convert a protobuf component data message to a sensor data object.

    Args:
        message: The protobuf message to convert.
        metrics: If not `None`, only the specified metrics will be retrieved.
            Otherwise all available metrics will be retrieved.

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
            if metrics is None or sample.sensor_metric in metrics
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
