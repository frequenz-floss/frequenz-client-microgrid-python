# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the microgrid metadata types."""

from collections.abc import Iterator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from frequenz.api.common.v1 import location_pb2

from frequenz.client.microgrid import Location
from frequenz.client.microgrid._location_proto import location_from_proto


@dataclass(frozen=True, kw_only=True)
class _ProtoConversionTestCase:  # pylint: disable=too-many-instance-attributes
    """Test case for protobuf conversion."""

    name: str
    """The description of the test case."""

    latitude: float
    """The latitude to set in the protobuf message."""

    longitude: float
    """The longitude to set in the protobuf message."""

    country_code: str
    """The country code to set in the protobuf message."""

    expected_none_latitude: bool = False
    """The latitude is expected to be None."""

    expected_none_longitude: bool = False
    """The longitude is expected to be None."""

    expected_none_country_code: bool = False
    """The country code is expected to be None."""

    expect_warning: bool = False
    """Whether to expect a warning during conversion."""


@pytest.fixture
def timezone_finder() -> Iterator[MagicMock]:
    """Return a mock timezone finder."""
    with patch(
        "frequenz.client.microgrid._location._timezone_finder", autospec=True
    ) as mock_timezone_finder:
        yield mock_timezone_finder


def test_timezone_not_looked_up_if_unused(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.latitude == 52.52
    assert location.longitude == 13.405
    assert location.country_code == "DE"
    timezone_finder.timezone_at.assert_not_called()


def test_timezone_looked_up_but_not_found(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    timezone_finder.timezone_at.return_value = None

    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.timezone is None
    timezone_finder.timezone_at.assert_called_once_with(lat=52.52, lng=13.405)


def test_timezone_looked_up_and_found(timezone_finder: MagicMock) -> None:
    """Test the location timezone is not looked up if it is not used."""
    timezone_finder.timezone_at.return_value = "Europe/Berlin"

    location = Location(latitude=52.52, longitude=13.405, country_code="DE")

    assert location.timezone == ZoneInfo(key="Europe/Berlin")
    timezone_finder.timezone_at.assert_called_once_with(lat=52.52, lng=13.405)


@pytest.mark.parametrize(
    "case",
    [
        _ProtoConversionTestCase(
            name="valid",
            latitude=52.52,
            longitude=13.405,
            country_code="DE",
        ),
        _ProtoConversionTestCase(
            name="boundary_latitude",
            latitude=90.0,
            longitude=13.405,
            country_code="DE",
        ),
        _ProtoConversionTestCase(
            name="boundary_longitude",
            latitude=52.52,
            longitude=180.0,
            country_code="DE",
        ),
        _ProtoConversionTestCase(
            name="invalid_latitude",
            latitude=91.0,
            longitude=13.405,
            country_code="DE",
            expected_none_latitude=True,
            expect_warning=True,
        ),
        _ProtoConversionTestCase(
            name="invalid_longitude",
            latitude=52.52,
            longitude=181.0,
            country_code="DE",
            expected_none_longitude=True,
            expect_warning=True,
        ),
        _ProtoConversionTestCase(
            name="empty_country_code",
            latitude=52.52,
            longitude=13.405,
            country_code="",
            expected_none_country_code=True,
            expect_warning=True,
        ),
        _ProtoConversionTestCase(
            name="all_invalid",
            latitude=-91.0,
            longitude=181.0,
            country_code="",
            expected_none_latitude=True,
            expected_none_longitude=True,
            expected_none_country_code=True,
            expect_warning=True,
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(
    caplog: pytest.LogCaptureFixture, case: _ProtoConversionTestCase
) -> None:
    """Test conversion from protobuf message to Location."""
    proto = location_pb2.Location(
        latitude=case.latitude,
        longitude=case.longitude,
        country_code=case.country_code,
    )
    with caplog.at_level("WARNING"):
        location = location_from_proto(proto)

    if case.expected_none_latitude:
        assert location.latitude is None
    else:
        assert location.latitude == pytest.approx(case.latitude)

    if case.expected_none_longitude:
        assert location.longitude is None
    else:
        assert location.longitude == pytest.approx(case.longitude)

    if case.expected_none_country_code:
        assert location.country_code is None
    else:
        assert location.country_code == case.country_code

    if case.expect_warning:
        assert len(caplog.records) > 0
        assert "Found issues in location:" in caplog.records[0].message
    else:
        assert len(caplog.records) == 0
