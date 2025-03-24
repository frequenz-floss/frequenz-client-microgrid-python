# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid metadata types."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from frequenz.client.microgrid import Location, Metadata, MicrogridId


@pytest.fixture
def timezone_finder() -> Iterator[MagicMock]:
    """Return a mock timezone finder."""
    with patch(
        "frequenz.client.microgrid._metadata._timezone_finder", autospec=True
    ) as mock_timezone_finder:
        yield mock_timezone_finder


@pytest.mark.parametrize(
    "latitude, longitude, timezone",
    [
        (None, None, None),
        (52.52, None, None),
        (None, 13.405, None),
        (None, None, ZoneInfo(key="UTC")),
        (52.52, None, ZoneInfo(key="UTC")),
        (None, 13.405, ZoneInfo(key="UTC")),
        (52.52, 13.405, ZoneInfo(key="UTC")),
    ],
    ids=str,
)
def test_location_timezone_not_looked_up_if_not_possible_or_necessary(
    timezone_finder: MagicMock,
    latitude: float | None,
    longitude: float | None,
    timezone: ZoneInfo | None,
) -> None:
    """Test the location timezone is not looked up if is not necessary or possible."""
    timezone_finder.timezone_at.return_value = "Europe/Berlin"

    location = Location(latitude=latitude, longitude=longitude, timezone=timezone)

    assert location.latitude == latitude
    assert location.longitude == longitude
    assert location.timezone == timezone
    timezone_finder.timezone_at.assert_not_called()


@pytest.mark.parametrize("timezone", [None, "Europe/Berlin"], ids=str)
def test_location_timezone_lookup(
    timezone_finder: MagicMock, timezone: str | None
) -> None:
    """Test the location timezone is looked up if not provided and there is enough info."""
    timezone_finder.timezone_at.return_value = timezone

    location = Location(latitude=52.52, longitude=13.405)

    if timezone is None:
        assert location.timezone is None
    else:
        assert location.timezone == ZoneInfo(key=timezone)
    timezone_finder.timezone_at.assert_called_once_with(lat=52.52, lng=13.405)


def test_metadata_initialization() -> None:
    """Test initialization of Metadata class."""
    # Test with no parameters
    metadata = Metadata()
    assert metadata.microgrid_id is None
    assert metadata.location is None

    # Test with only microgrid_id
    microgrid_id = MicrogridId(42)
    metadata = Metadata(microgrid_id=microgrid_id)
    assert metadata.microgrid_id == microgrid_id
    assert metadata.location is None

    # Test with only location
    location = Location(latitude=52.52, longitude=13.405)
    metadata = Metadata(location=location)
    assert metadata.microgrid_id is None
    assert metadata.location == location

    # Test with both parameters
    metadata = Metadata(microgrid_id=microgrid_id, location=location)
    assert metadata.microgrid_id == microgrid_id
    assert metadata.location == location


def test_metadata_microgrid_id_validation() -> None:
    """Test validation of microgrid_id in Metadata class."""
    # Valid microgrid_id should work
    metadata = Metadata(microgrid_id=MicrogridId(0))
    assert metadata.microgrid_id == MicrogridId(0)

    metadata = Metadata(microgrid_id=MicrogridId(42))
    assert metadata.microgrid_id == MicrogridId(42)

    # None should be accepted as a valid value
    metadata = Metadata(microgrid_id=None)
    assert metadata.microgrid_id is None

    # Negative IDs should raise ValueError
    with pytest.raises(ValueError):
        Metadata(microgrid_id=MicrogridId(-1))
