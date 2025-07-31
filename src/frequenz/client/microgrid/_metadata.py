# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Metadata that describes a microgrid."""

from dataclasses import dataclass
from zoneinfo import ZoneInfo

from frequenz.client.common.microgrid import MicrogridId


@dataclass(frozen=True, kw_only=True)
class Location:
    """Metadata for the location of microgrid."""

    latitude: float | None = None
    """The latitude of the microgrid in degree."""

    longitude: float | None = None
    """The longitude of the microgrid in degree."""

    timezone: ZoneInfo | None = None
    """The timezone of the microgrid."""


@dataclass(frozen=True, kw_only=True)
class Metadata:
    """Metadata for the microgrid."""

    microgrid_id: MicrogridId | None = None
    """The ID of the microgrid."""

    location: Location | None = None
    """The location of the microgrid."""
