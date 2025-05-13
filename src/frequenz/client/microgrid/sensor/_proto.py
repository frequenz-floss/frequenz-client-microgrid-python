# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of Sensor objects from protobuf messages."""

import logging
from typing import assert_never

from frequenz.api.common.components_pb2 import ComponentCategory as PbComponentCategory
from frequenz.api.microgrid import microgrid_pb2

from frequenz.client.microgrid._component import ComponentCategory

from .._id import SensorId
from .._lifetime import Lifetime
from .._util import enum_from_proto
from ._accelerometer import Accelerometer
from ._anemometer import Anemometer
from ._barometer import Barometer
from ._category import SensorCategory
from ._general_sensor import GeneralSensor
from ._hygrometer import Hygrometer
from ._problematic import (
    MismatchedCategorySensor,
    UnrecognizedSensor,
    UnspecifiedSensor,
)
from ._pyranometer import Pyranometer
from ._thermometer import Thermometer
from ._types import SensorTypes

_logger = logging.getLogger(__name__)


def sensor_from_proto(message: microgrid_pb2.Component) -> SensorTypes:
    """Convert a protobuf message to a `SensorTypes` instance.

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
) -> SensorTypes:
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

    # Check the component category is the expected sensor category
    category_is_wrong = False
    if message.category is not PbComponentCategory.COMPONENT_CATEGORY_SENSOR:
        major_issues.append(f"unexpected category for sensor ({message.category})")
        category_is_wrong = True

    # Get the sensor category from the component sensor metadata
    metadata = message.WhichOneof("metadata")
    if metadata != "sensor":
        major_issues.append(f"wrong sensor metadata ({metadata!r})")
        if category_is_wrong:
            return MismatchedCategorySensor(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
                category=SensorCategory.UNSPECIFIED,
                component_category=enum_from_proto(message.category, ComponentCategory),
            )
        return UnspecifiedSensor(
            id=sensor_id,
            name=name,
            manufacturer=manufacturer,
            model_name=model_name,
            operational_lifetime=Lifetime(),
        )

    category = enum_from_proto(message.sensor.type, SensorCategory)
    match category:
        case SensorCategory.UNSPECIFIED:
            major_issues.append("category is unspecified")
            return UnspecifiedSensor(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case int():
            major_issues.append("category is unrecognized")
            return UnrecognizedSensor(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                category=category,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.ACCELEROMETER:
            return Accelerometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.ANEMOMETER:
            return Anemometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.BAROMETER:
            return Barometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.GENERAL:
            return GeneralSensor(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.HYGROMETER:
            return Hygrometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.PYRANOMETER:
            return Pyranometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case SensorCategory.THERMOMETER:
            return Thermometer(
                id=sensor_id,
                name=name,
                manufacturer=manufacturer,
                model_name=model_name,
                operational_lifetime=Lifetime(),
            )
        case unexpected_category:
            assert_never(unexpected_category)
