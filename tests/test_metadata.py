# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid metadata types."""

from zoneinfo import ZoneInfo

import pytest
from frequenz.client.common.microgrid import MicrogridId

from frequenz.client.microgrid import Location, Metadata


@pytest.mark.parametrize("latitude", [None, 52.52], ids=str)
@pytest.mark.parametrize("longitude", [None, 13.405], ids=str)
@pytest.mark.parametrize("timezone", [None, ZoneInfo(key="UTC")], ids=str)
def test_location_initialization(
    latitude: float | None,
    longitude: float | None,
    timezone: ZoneInfo | None,
) -> None:
    """Test location initialization with different combinations of parameters."""
    location = Location(latitude=latitude, longitude=longitude, timezone=timezone)

    assert location.latitude == latitude
    assert location.longitude == longitude
    assert location.timezone == timezone


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

    # Test with only location - timezone should be None even with lat/lng
    location = Location(latitude=52.52, longitude=13.405)
    metadata = Metadata(location=location)
    assert metadata.microgrid_id is None
    assert metadata.location == location
    assert metadata.location.timezone is None

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
