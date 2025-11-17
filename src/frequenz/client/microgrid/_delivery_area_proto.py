# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of DeliveryArea objects from protobuf messages."""

import logging

from frequenz.api.common.v1alpha8.grid import delivery_area_pb2

from ._delivery_area import DeliveryArea, EnergyMarketCodeType
from ._util import enum_from_proto

_logger = logging.getLogger(__name__)


def delivery_area_from_proto(message: delivery_area_pb2.DeliveryArea) -> DeliveryArea:
    """Convert a protobuf delivery area message to a delivery area object.

    Args:
        message: The protobuf message to convert.

    Returns:
        The resulting delivery area object.
    """
    issues: list[str] = []

    code = message.code or None
    if code is None:
        issues.append("code is empty")

    code_type = enum_from_proto(message.code_type, EnergyMarketCodeType)
    if code_type is EnergyMarketCodeType.UNSPECIFIED:
        issues.append("code_type is unspecified")
    elif isinstance(code_type, int):
        issues.append("code_type is unrecognized")

    if issues:
        _logger.warning(
            "Found issues in delivery area: %s | Protobuf message:\n%s",
            ", ".join(issues),
            message,
        )

    return DeliveryArea(code=code, code_type=code_type)
