# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading of ComponentConnection objects from protobuf messages."""

import logging

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.common.microgrid.components import ComponentId

from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from ._connection import ComponentConnection

_logger = logging.getLogger(__name__)


def component_connection_from_proto(
    message: electrical_components_pb2.ElectricalComponentConnection,
) -> ComponentConnection | None:
    """Create a `ComponentConnection` from a protobuf message."""
    major_issues: list[str] = []
    minor_issues: list[str] = []

    connection = component_connection_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in component connection: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in component connection: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return connection


def component_connection_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponentConnection,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ComponentConnection | None:
    """Create a `ComponentConnection` from a protobuf message collecting issues.

    This function is useful when you want to collect issues during the parsing
    of multiple connections, rather than logging them immediately.

    Args:
        message: The protobuf message to parse.
        major_issues: A list to collect major issues found during parsing.
        minor_issues: A list to collect minor issues found during parsing.

    Returns:
        A `ComponentConnection` object created from the protobuf message, or
            `None` if the protobuf message is completely invalid and a
            `ComponentConnection` cannot be created.
    """
    source_component_id = ComponentId(message.source_electrical_component_id)
    destination_component_id = ComponentId(message.destination_electrical_component_id)
    if source_component_id == destination_component_id:
        major_issues.append(
            f"connection ignored: source and destination are the same ({source_component_id})",
        )
        return None

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    return ComponentConnection(
        source=source_component_id,
        destination=destination_component_id,
        operational_lifetime=lifetime,
    )


def _get_operational_lifetime_from_proto(
    message: electrical_components_pb2.ElectricalComponentConnection,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Lifetime:
    """Get the operational lifetime from a protobuf message."""
    if message.HasField("operational_lifetime"):
        try:
            return lifetime_from_proto(message.operational_lifetime)
        except ValueError as exc:
            major_issues.append(
                f"invalid operational lifetime ({exc}), considering it as missing "
                "(i.e. always operational)",
            )
    else:
        minor_issues.append(
            "missing operational lifetime, considering it always operational",
        )
    return Lifetime()
