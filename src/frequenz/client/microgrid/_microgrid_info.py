# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Definition of a microgrid."""

import datetime
import enum
import logging
from dataclasses import dataclass
from functools import cached_property

from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId

from ._delivery_area import DeliveryArea
from ._location import Location

_logger = logging.getLogger(__name__)


@enum.unique
class MicrogridStatus(enum.Enum):
    """The possible statuses for a microgrid."""

    UNSPECIFIED = microgrid_pb2.MICROGRID_STATUS_UNSPECIFIED
    """The status is unspecified. This should not be used."""

    ACTIVE = microgrid_pb2.MICROGRID_STATUS_ACTIVE
    """The microgrid is active."""

    INACTIVE = microgrid_pb2.MICROGRID_STATUS_INACTIVE
    """The microgrid is inactive."""


@dataclass(frozen=True, kw_only=True)
class MicrogridInfo:
    """A localized grouping of electricity generation, energy storage, and loads.

    A microgrid is a localized grouping of electricity generation, energy storage, and
    loads that normally operates connected to a traditional centralized grid.

    Each microgrid has a unique identifier and is associated with an enterprise account.

    A key feature is that it has a physical location and is situated in a delivery area.

    Note: Key Concepts
        - Physical Location: Geographical coordinates specify the exact physical
          location of the microgrid.
        - Delivery Area: Each microgrid is part of a broader delivery area, which is
          crucial for energy trading and compliance.
    """

    id: MicrogridId
    """The unique identifier of the microgrid."""

    enterprise_id: EnterpriseId
    """The unique identifier linking this microgrid to its parent enterprise account."""

    name: str | None
    """Name of the microgrid."""

    delivery_area: DeliveryArea | None
    """The delivery area where the microgrid is located, as identified by a specific code."""

    location: Location | None
    """Physical location of the microgrid, in geographical co-ordinates."""

    status: MicrogridStatus | int
    """The current status of the microgrid."""

    create_timestamp: datetime.datetime
    """The UTC timestamp indicating when the microgrid was initially created."""

    @cached_property
    def is_active(self) -> bool:
        """Whether the microgrid is active."""
        if self.status is MicrogridStatus.UNSPECIFIED:
            # Because this is a cached property, the warning will only be logged once.
            _logger.warning(
                "Microgrid %s has an unspecified status. Assuming it is active.", self
            )
        return self.status in (MicrogridStatus.ACTIVE, MicrogridStatus.UNSPECIFIED)

    def __str__(self) -> str:
        """Return the ID of this microgrid as a string."""
        name = f":{self.name}" if self.name else ""
        return f"{self.id}{name}"
