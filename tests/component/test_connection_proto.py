# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests conversion from protobuf messages to ComponentConnection."""

import logging
from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, patch

import pytest
from frequenz.api.common.v1.microgrid import lifetime_pb2
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf import timestamp_pb2

from frequenz.client.microgrid.component import ComponentConnection
from frequenz.client.microgrid.component._connection_proto import (
    component_connection_from_proto,
    component_connection_from_proto_with_issues,
)


@pytest.mark.parametrize(
    "proto_data, expected_minor_issues",
    [
        pytest.param(
            {
                "source_component_id": 1,
                "destination_component_id": 2,
                "has_lifetime": True,
            },
            [],
            id="full",
        ),
        pytest.param(
            {
                "source_component_id": 1,
                "destination_component_id": 2,
                "has_lifetime": False,
            },
            ["missing operational lifetime, considering it always operational"],
            id="no_lifetime",
        ),
    ],
)
def test_success(proto_data: dict[str, Any], expected_minor_issues: list[str]) -> None:
    """Test successful conversion from protobuf message to ComponentConnection."""
    proto = components_pb2.ComponentConnection(
        source_component_id=proto_data["source_component_id"],
        destination_component_id=proto_data["destination_component_id"],
    )

    if proto_data["has_lifetime"]:
        now = datetime.now(timezone.utc)
        start_time = timestamp_pb2.Timestamp()
        start_time.FromDatetime(now)
        lifetime = lifetime_pb2.Lifetime()
        lifetime.start_timestamp.CopyFrom(start_time)
        proto.operational_lifetime.CopyFrom(lifetime)

    major_issues: list[str] = []
    minor_issues: list[str] = []
    connection = component_connection_from_proto_with_issues(
        proto,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert connection is not None
    assert not major_issues
    assert minor_issues == expected_minor_issues
    assert connection.source == ComponentId(proto_data["source_component_id"])
    assert connection.destination == ComponentId(proto_data["destination_component_id"])


def test_error_same_ids() -> None:
    """Test proto conversion with same source and destination returns None."""
    proto = components_pb2.ComponentConnection(
        source_component_id=1, destination_component_id=1
    )

    major_issues: list[str] = []
    minor_issues: list[str] = []
    conn = component_connection_from_proto_with_issues(
        proto,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    assert conn is None
    assert major_issues == [
        "connection ignored: source and destination are the same (CID1)"
    ]
    assert not minor_issues


@patch(
    "frequenz.client.microgrid.component._connection_proto.lifetime_from_proto",
    autospec=True,
)
def test_invalid_lifetime(mock_lifetime_from_proto: Mock) -> None:
    """Test proto conversion with invalid lifetime data."""
    mock_lifetime_from_proto.side_effect = ValueError("Invalid lifetime")

    proto = components_pb2.ComponentConnection(
        source_component_id=1, destination_component_id=2
    )
    now = datetime.now(timezone.utc)
    start_time = timestamp_pb2.Timestamp()
    start_time.FromDatetime(now)
    lifetime = lifetime_pb2.Lifetime()
    lifetime.start_timestamp.CopyFrom(start_time)
    proto.operational_lifetime.CopyFrom(lifetime)

    major_issues: list[str] = []
    minor_issues: list[str] = []
    connection = component_connection_from_proto_with_issues(
        proto, major_issues=major_issues, minor_issues=minor_issues
    )

    assert connection is not None
    assert connection.source == ComponentId(1)
    assert connection.destination == ComponentId(2)
    assert major_issues == [
        "invalid operational lifetime (Invalid lifetime), considering it as missing "
        "(i.e. always operational)"
    ]
    assert not minor_issues
    mock_lifetime_from_proto.assert_called_once_with(proto.operational_lifetime)


@patch(
    "frequenz.client.microgrid.component._connection_proto."
    "component_connection_from_proto_with_issues",
    autospec=True,
)
def test_issues_logging(
    mock_from_proto_with_issues: Mock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test collection and logging of issues during proto conversion."""
    caplog.set_level("DEBUG")  # Ensure we capture DEBUG level messages

    # mypy needs the explicit return
    def _fake_from_proto_with_issues(  # pylint: disable=useless-return
        _: components_pb2.ComponentConnection,
        *,
        major_issues: list[str],
        minor_issues: list[str],
    ) -> ComponentConnection | None:
        """Fake function to simulate conversion and logging."""
        major_issues.append("fake major issue")
        minor_issues.append("fake minor issue")
        return None

    mock_from_proto_with_issues.side_effect = _fake_from_proto_with_issues

    mock_proto = Mock(name="proto", spec=components_pb2.ComponentConnection)
    connection = component_connection_from_proto(mock_proto)

    assert connection is None
    assert caplog.record_tuples == [
        (
            "frequenz.client.microgrid.component._connection_proto",
            logging.WARNING,
            "Found issues in component connection: fake major issue | "
            f"Protobuf message:\n{mock_proto}",
        ),
        (
            "frequenz.client.microgrid.component._connection_proto",
            logging.DEBUG,
            "Found minor issues in component connection: fake minor issue | "
            f"Protobuf message:\n{mock_proto}",
        ),
    ]
