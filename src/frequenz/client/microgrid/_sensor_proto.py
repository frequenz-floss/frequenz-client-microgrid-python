# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of SensorDataSamples objects from protobuf messages."""

import logging

from frequenz.api.common import components_pb2
from frequenz.api.microgrid import microgrid_pb2

from ._id import SensorId
from ._lifetime import Lifetime
from .sensor import Sensor

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
