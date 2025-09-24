# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of Location objects from protobuf messages."""

import logging

from frequenz.api.common.v1alpha8.types import location_pb2

from ._location import Location

_logger = logging.getLogger(__name__)


def location_from_proto(message: location_pb2.Location) -> Location:
    """Convert a protobuf location message to a location object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting location object.
    """
    issues: list[str] = []

    latitude: float | None = message.latitude if -90 <= message.latitude <= 90 else None
    if latitude is None:
        issues.append("latitude out of range [-90, 90]")

    longitude: float | None = (
        message.longitude if -180 <= message.longitude <= 180 else None
    )
    if longitude is None:
        issues.append("longitude out of range [-180, 180]")

    country_code = message.country_code or None
    if country_code is None:
        issues.append("country code is empty")

    if issues:
        _logger.warning(
            "Found issues in location: %s | Protobuf message:\n%s",
            ", ".join(issues),
            message,
        )

    return Location(latitude=latitude, longitude=longitude, country_code=country_code)
