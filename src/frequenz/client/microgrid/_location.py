# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Location information for a microgrid."""


import logging
from dataclasses import dataclass
from functools import cached_property
from zoneinfo import ZoneInfo

import timezonefinder

_timezone_finder = timezonefinder.TimezoneFinder()
_logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class Location:
    """A location of a microgrid."""

    latitude: float | None
    """The latitude of the microgrid in degree."""

    longitude: float | None
    """The longitude of the microgrid in degree."""

    country_code: str | None
    """The country code of the microgrid in ISO 3166-1 Alpha 2 format."""

    @cached_property
    def timezone(self) -> ZoneInfo | None:
        """The timezone of the microgrid, or `None` if it could not be determined."""
        if self.latitude is None or self.longitude is None:
            _logger.warning(
                "Latitude (%s) or longitude (%s) missing, cannot determine timezone"
            )
            return None
        timezone = _timezone_finder.timezone_at(lat=self.latitude, lng=self.longitude)
        return ZoneInfo(key=timezone) if timezone else None

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        country = self.country_code or "<NO COUNTRY CODE>"
        lat = f"{self.latitude:.2f}" if self.latitude is not None else "?"
        lon = f"{self.longitude:.2f}" if self.longitude is not None else "?"
        coordinates = ""
        if self.latitude is not None or self.longitude is not None:
            coordinates = f":({lat}, {lon})"
        return f"{country}{coordinates}"
