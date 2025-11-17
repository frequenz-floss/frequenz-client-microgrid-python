# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for MicrogridInfo class."""

from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common.v1alpha8.grid import delivery_area_pb2
from frequenz.api.common.v1alpha8.microgrid import microgrid_pb2
from frequenz.client.common.microgrid import EnterpriseId, MicrogridId

from frequenz.client.microgrid import (
    DeliveryArea,
    EnergyMarketCodeType,
    Location,
    MicrogridInfo,
    MicrogridStatus,
)
from frequenz.client.microgrid._microgrid_info_proto import microgrid_info_from_proto


@dataclass(frozen=True, kw_only=True)
class _ProtoConversionTestCase:
    """Test case for protobuf conversion."""

    name: str
    """Description of the test case."""

    has_delivery_area: bool
    """Whether to include delivery area in the protobuf message."""

    has_location: bool
    """Whether to include location in the protobuf message."""

    has_name: bool
    """Whether to include name in the protobuf message."""

    status: MicrogridStatus | int
    """The status to set in the protobuf message."""

    expected_log: tuple[str, str] | None = None
    """Whether to expect a log during conversion (level, message)."""


def test_creation() -> None:
    """Test MicrogridInfo creation with all fields."""
    now = datetime.now(timezone.utc)
    info = MicrogridInfo(
        id=MicrogridId(1234),
        enterprise_id=EnterpriseId(5678),
        name="Test Microgrid",
        delivery_area=DeliveryArea(
            code="DE123", code_type=EnergyMarketCodeType.EUROPE_EIC
        ),
        location=Location(latitude=52.52, longitude=13.405, country_code="DE"),
        status=MicrogridStatus.ACTIVE,
        create_timestamp=now,
    )

    assert info.id == MicrogridId(1234)
    assert info.enterprise_id == EnterpriseId(5678)
    assert info.name == "Test Microgrid"
    assert info.delivery_area is not None
    assert info.delivery_area.code == "DE123"
    assert info.delivery_area.code_type == EnergyMarketCodeType.EUROPE_EIC
    assert info.location is not None
    assert info.location.latitude is not None
    assert info.location.latitude == pytest.approx(52.52)
    assert info.location.longitude is not None
    assert info.location.longitude == pytest.approx(13.405)
    assert info.location.country_code == "DE"
    assert info.status == MicrogridStatus.ACTIVE
    assert info.create_timestamp == now
    assert info.is_active is True


def test_creation_without_optionals() -> None:
    """Test MicrogridInfo creation with only required fields."""
    now = datetime.now(timezone.utc)
    info = MicrogridInfo(
        id=MicrogridId(1234),
        enterprise_id=EnterpriseId(5678),
        name=None,
        delivery_area=None,
        location=None,
        status=MicrogridStatus.ACTIVE,
        create_timestamp=now,
    )

    assert info.id == MicrogridId(1234)
    assert info.enterprise_id == EnterpriseId(5678)
    assert info.name is None
    assert info.delivery_area is None
    assert info.location is None
    assert info.status == MicrogridStatus.ACTIVE
    assert info.create_timestamp == now
    assert info.is_active is True


@pytest.mark.parametrize(
    "status,expected_active",
    [
        pytest.param(MicrogridStatus.ACTIVE, True, id="ACTIVE"),
        pytest.param(MicrogridStatus.INACTIVE, False, id="INACTIVE"),
        pytest.param(MicrogridStatus.UNSPECIFIED, True, id="UNSPECIFIED"),
    ],
)
def test_is_active_property(status: MicrogridStatus, expected_active: bool) -> None:
    """Test the is_active property for different status values."""
    now = datetime.now(timezone.utc)
    info = MicrogridInfo(
        id=MicrogridId(1234),
        enterprise_id=EnterpriseId(5678),
        name=None,
        delivery_area=None,
        location=None,
        status=status,
        create_timestamp=now,
    )
    assert info.is_active is expected_active


@pytest.mark.parametrize(
    "name,expected_str",
    [
        pytest.param("Test Grid", "MID1234:Test Grid", id="with-name"),
        pytest.param(None, "MID1234", id="none-name"),
        pytest.param("", "MID1234", id="empty-name"),
    ],
)
def test_str(name: str | None, expected_str: str) -> None:
    """Test string representation of MicrogridInfo."""
    now = datetime.now(timezone.utc)
    info = MicrogridInfo(
        id=MicrogridId(1234),
        enterprise_id=EnterpriseId(5678),
        name=name,
        delivery_area=None,
        location=None,
        status=MicrogridStatus.ACTIVE,
        create_timestamp=now,
    )
    assert str(info) == expected_str


@pytest.mark.parametrize(
    "case",
    [
        _ProtoConversionTestCase(
            name="full",
            has_delivery_area=True,
            has_location=True,
            has_name=True,
            status=MicrogridStatus.ACTIVE,
        ),
        _ProtoConversionTestCase(
            name="no_delivery_area",
            has_delivery_area=False,
            has_location=True,
            has_name=True,
            status=MicrogridStatus.ACTIVE,
            expected_log=(
                "WARNING",
                "Found issues in microgrid: delivery_area is missing",
            ),
        ),
        _ProtoConversionTestCase(
            name="no_location",
            has_delivery_area=True,
            has_location=False,
            has_name=True,
            status=MicrogridStatus.ACTIVE,
            expected_log=("WARNING", "Found issues in microgrid: location is missing"),
        ),
        _ProtoConversionTestCase(
            name="empty_name",
            has_delivery_area=True,
            has_location=True,
            has_name=False,
            status=MicrogridStatus.ACTIVE,
            expected_log=("DEBUG", "Found minor issues in microgrid: name is empty"),
        ),
        _ProtoConversionTestCase(
            name="unspecified_status",
            has_delivery_area=True,
            has_location=True,
            has_name=True,
            status=MicrogridStatus.UNSPECIFIED,
            expected_log=(
                "WARNING",
                "Found issues in microgrid: status is unspecified",
            ),
        ),
        _ProtoConversionTestCase(
            name="unrecognized_status",
            has_delivery_area=True,
            has_location=True,
            has_name=True,
            status=999,  # Unknown status value
            expected_log=(
                "WARNING",
                "Found issues in microgrid: status is unrecognized",
            ),
        ),
    ],
    ids=lambda case: case.name,
)
@patch("frequenz.client.microgrid._microgrid_info_proto.delivery_area_from_proto")
@patch("frequenz.client.microgrid._microgrid_info_proto.location_from_proto")
@patch("frequenz.client.microgrid._microgrid_info_proto.enum_from_proto")
@patch("frequenz.client.microgrid._microgrid_info_proto.conversion.to_datetime")
# pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-branches
def test_from_proto(
    mock_to_datetime: Mock,
    mock_enum_from_proto: Mock,
    mock_location_from_proto: Mock,
    mock_delivery_area_from_proto: Mock,
    caplog: pytest.LogCaptureFixture,
    case: _ProtoConversionTestCase,
) -> None:
    """Test conversion from protobuf message to MicrogridInfo."""
    now = datetime.now(timezone.utc)
    mock_to_datetime.return_value = now

    if isinstance(case.status, MicrogridStatus):
        mock_enum_from_proto.return_value = case.status
    else:
        mock_enum_from_proto.return_value = case.status

    mock_location = (
        Location(
            latitude=52.52,
            longitude=13.405,
            country_code="DE",
        )
        if case.has_location
        else None
    )
    mock_location_from_proto.return_value = mock_location

    mock_delivery_area = (
        DeliveryArea(
            code="DE123",
            code_type=EnergyMarketCodeType.EUROPE_EIC,
        )
        if case.has_delivery_area
        else None
    )
    mock_delivery_area_from_proto.return_value = mock_delivery_area

    proto = microgrid_pb2.Microgrid(
        id=1234,
        enterprise_id=5678,
        name="Test Grid" if case.has_name else "",
        # We use a ignore because we want to pass an arbitrary int here
        status=(
            case.status.value  # type: ignore[arg-type]
            if isinstance(case.status, MicrogridStatus)
            else case.status
        ),
    )

    # Add optional fields if needed
    if case.has_delivery_area:
        proto.delivery_area.code = "DE123"
        proto.delivery_area.code_type = (
            delivery_area_pb2.EnergyMarketCodeType.ENERGY_MARKET_CODE_TYPE_EUROPE_EIC
        )

    if case.has_location:
        proto.location.latitude = 52.52
        proto.location.longitude = 13.405
        proto.location.country_code = "DE"

    # Run the conversion
    with caplog.at_level("DEBUG"):
        info = microgrid_info_from_proto(proto)

    # Verify the result
    assert info.id == MicrogridId(1234)
    assert info.enterprise_id == EnterpriseId(5678)
    assert info.create_timestamp == now

    if case.has_name:
        assert info.name == "Test Grid"
    else:
        assert info.name is None

    # Verify mock calls
    mock_to_datetime.assert_called_once_with(proto.create_timestamp)
    mock_enum_from_proto.assert_called_once_with(proto.status, MicrogridStatus)

    if case.has_delivery_area:
        mock_delivery_area_from_proto.assert_called_once_with(proto.delivery_area)
        assert info.delivery_area == mock_delivery_area
    else:
        mock_delivery_area_from_proto.assert_not_called()
        assert info.delivery_area is None

    if case.has_location:
        mock_location_from_proto.assert_called_once_with(proto.location)
        assert info.location == mock_location
    else:
        mock_location_from_proto.assert_not_called()
        assert info.location is None

    # Verify logging behavior
    if case.expected_log:
        expected_level, expected_message = case.expected_log
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == expected_level
        assert expected_message in caplog.records[0].message
    else:
        assert len(caplog.records) == 0
