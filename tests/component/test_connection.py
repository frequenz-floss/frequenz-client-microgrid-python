# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for ComponentConnection class and related functionality."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.component import ComponentConnection


def test_creation() -> None:
    """Test basic ComponentConnection creation and validation."""
    now = datetime.now(timezone.utc)
    lifetime = Lifetime(start=now)
    connection = ComponentConnection(
        source=ComponentId(1), destination=ComponentId(2), operational_lifetime=lifetime
    )

    assert connection.source == ComponentId(1)
    assert connection.destination == ComponentId(2)
    assert connection.operational_lifetime == lifetime


def test_validation() -> None:
    """Test validation of source and destination components."""
    with pytest.raises(
        ValueError, match="Source and destination components must be different"
    ):
        ComponentConnection(source=ComponentId(1), destination=ComponentId(1))


def test_str() -> None:
    """Test string representation of ComponentConnection."""
    connection = ComponentConnection(source=ComponentId(1), destination=ComponentId(2))
    assert str(connection) == "CID1->CID2"


@pytest.mark.parametrize(
    "lifetime_active", [True, False], ids=["operational", "not-operational"]
)
def test_is_operational_at(lifetime_active: bool) -> None:
    """Test active_at behavior with lifetime.active values."""
    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.is_operational_at.return_value = lifetime_active

    connection = ComponentConnection(
        source=ComponentId(1),
        destination=ComponentId(2),
        operational_lifetime=mock_lifetime,
    )

    now = datetime.now(timezone.utc)
    assert connection.is_operational_at(now) == lifetime_active
    mock_lifetime.is_operational_at.assert_called_once_with(now)


@patch("frequenz.client.microgrid.component._connection.datetime")
@pytest.mark.parametrize(
    "lifetime_active", [True, False], ids=["operational", "not-operational"]
)
def test_is_operational_now(mock_datetime: Mock, lifetime_active: bool) -> None:
    """Test if the connection is operational at the current time."""
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.side_effect = lambda tz: now.replace(tzinfo=tz)
    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.is_operational_at.return_value = lifetime_active

    connection = ComponentConnection(
        source=ComponentId(1),
        destination=ComponentId(2),
        operational_lifetime=mock_lifetime,
    )

    assert connection.is_operational_now() is lifetime_active
    mock_lifetime.is_operational_at.assert_called_once_with(now)
    mock_datetime.now.assert_called_once_with(timezone.utc)
