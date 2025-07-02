# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Status for a component."""

import enum

from frequenz.api.common.v1.microgrid.components import components_pb2


@enum.unique
class ComponentStatus(enum.Enum):
    """The known statuses of a component."""

    UNSPECIFIED = components_pb2.COMPONENT_STATUS_UNSPECIFIED
    """The status is unspecified."""

    ACTIVE = components_pb2.COMPONENT_STATUS_ACTIVE
    """The component is active."""

    INACTIVE = components_pb2.COMPONENT_STATUS_INACTIVE
    """The component is inactive."""
