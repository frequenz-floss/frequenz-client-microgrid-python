# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Location information for a microgrid."""


from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Location:
    """A location of a microgrid."""

    latitude: float | None
    """The latitude of the microgrid in degree."""

    longitude: float | None
    """The longitude of the microgrid in degree."""

    country_code: str | None
    """The country code of the microgrid in ISO 3166-1 Alpha 2 format."""

    def __str__(self) -> str:
        """Return the short string representation of this instance."""
        country = self.country_code or "<NO COUNTRY CODE>"
        lat = f"{self.latitude:.2f}" if self.latitude is not None else "?"
        lon = f"{self.longitude:.2f}" if self.longitude is not None else "?"
        coordinates = ""
        if self.latitude is not None or self.longitude is not None:
            coordinates = f":({lat}, {lon})"
        return f"{country}{coordinates}"
