# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Lifetime class and its protobuf conversion."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import pytest
from frequenz.api.common.v1.microgrid import lifetime_pb2
from google.protobuf import timestamp_pb2

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid._lifetime_proto import lifetime_from_proto


class _Time(Enum):
    """Types of time points used in tests."""

    PAST = auto()
    """A time point in the past."""

    NOW = auto()
    """The current time point."""

    FUTURE = auto()
    """A time point in the future."""


@dataclass(frozen=True, kw_only=True)
class _LifetimeTestCase:
    """Test case for Lifetime creation and validation."""

    name: str
    """The description of the test case."""

    start: bool
    """Whether to include start time."""

    end: bool
    """Whether to include end time."""

    expected_start: bool
    """Whether start should be set."""

    expected_end: bool
    """Whether end should be set."""

    expected_operational: bool
    """The expected operational state."""


@dataclass(frozen=True, kw_only=True)
class _ActivityTestCase:
    """Test case for Lifetime activity state."""

    name: str
    """The description of the test case."""

    start_type: _Time | None
    """The type of start time."""

    end_type: _Time | None
    """The type of end time."""

    expected_operational: bool
    """The expected operational state."""


@dataclass(frozen=True, kw_only=True)
class _ProtoConversionTestCase:
    """Test case for protobuf conversion."""

    name: str
    """The description of the test case."""

    include_start: bool
    """Whether to include start timestamp."""

    include_end: bool
    """Whether to include end timestamp."""


@dataclass(frozen=True, kw_only=True)
class _FixedLifetimeTestCase:
    """Test case for fixed lifetime activity testing."""

    name: str
    """The description of the test case."""

    test_time: _Time
    """The type of time point to test."""

    expected_operational: bool
    """The expected operational state."""


@pytest.fixture
def now() -> datetime:
    """Fixture to provide current UTC time."""
    return datetime.now(timezone.utc)


@pytest.fixture
def past(now: datetime) -> datetime:
    """Fixture to provide a past time."""
    return now.replace(year=now.year - 1)


@pytest.fixture
def future(now: datetime) -> datetime:
    """Fixture to provide a future time."""
    return now.replace(year=now.year + 1)


@pytest.mark.parametrize(
    "case",
    [
        _LifetimeTestCase(
            name="full",
            start=True,
            end=True,
            expected_start=True,
            expected_end=True,
            expected_operational=True,
        ),
        _LifetimeTestCase(
            name="only_start",
            start=True,
            end=False,
            expected_start=True,
            expected_end=False,
            expected_operational=True,
        ),
        _LifetimeTestCase(
            name="only_end",
            start=False,
            end=True,
            expected_start=False,
            expected_end=True,
            expected_operational=True,
        ),
        _LifetimeTestCase(
            name="no_dates",
            start=False,
            end=False,
            expected_start=False,
            expected_end=False,
            expected_operational=True,
        ),
    ],
    ids=lambda case: case.name,
)
def test_creation(now: datetime, future: datetime, case: _LifetimeTestCase) -> None:
    """Test creating Lifetime instances with various parameters."""
    lifetime = Lifetime(
        start=now if case.start else None,
        end=future if case.end else None,
    )
    assert (lifetime.start is not None) == case.expected_start
    if case.expected_start:
        assert lifetime.start == now
    assert (lifetime.end is not None) == case.expected_end
    if case.expected_end:
        assert lifetime.end == future
    assert lifetime.is_operational_now() == case.expected_operational


@pytest.mark.parametrize("start", [None, *_Time], ids=lambda x: f"start_{x}")
@pytest.mark.parametrize("end", [None, *_Time], ids=lambda x: f"end_{x}")
def test_validation(
    past: datetime,
    now: datetime,
    future: datetime,
    start: _Time | None,
    end: _Time | None,
) -> None:
    """Test validation of Lifetime parameters."""
    time_map = {
        _Time.PAST: past,
        _Time.NOW: now,
        _Time.FUTURE: future,
        None: None,
    }

    start_time = time_map[start]
    end_time = time_map[end]

    # Invalid combinations are when end is before start
    should_fail = (
        start is not None
        and end is not None
        and (
            (start == _Time.NOW and end == _Time.PAST)
            or (start == _Time.FUTURE and end == _Time.PAST)
            or (start == _Time.FUTURE and end == _Time.NOW)
        )
    )

    if should_fail:
        with pytest.raises(ValueError, match="Start must be before or equal to end."):
            Lifetime(start=start_time, end=end_time)
    else:
        lifetime = Lifetime(start=start_time, end=end_time)
        # Verify the timestamps are set correctly
        assert lifetime.start == start_time
        assert lifetime.end == end_time


@pytest.mark.parametrize(
    "case",
    [
        _ActivityTestCase(
            name="past_start-no_end",
            start_type=_Time.PAST,
            end_type=None,
            expected_operational=True,
        ),
        _ActivityTestCase(
            name="past_start-future_end",
            start_type=_Time.PAST,
            end_type=_Time.FUTURE,
            expected_operational=True,
        ),
        _ActivityTestCase(
            name="future_start-no_end",
            start_type=_Time.FUTURE,
            end_type=None,
            expected_operational=False,
        ),
        _ActivityTestCase(
            name="past_start-past_end",
            start_type=_Time.PAST,
            end_type=_Time.PAST,
            expected_operational=False,
        ),
        _ActivityTestCase(
            name="now_start-no_end",
            start_type=_Time.NOW,
            end_type=None,
            expected_operational=True,
        ),
        _ActivityTestCase(
            name="no_start-now_end",
            start_type=None,
            end_type=_Time.NOW,
            expected_operational=True,
        ),
        _ActivityTestCase(
            name="now_start-now_end",
            start_type=_Time.NOW,
            end_type=_Time.NOW,
            expected_operational=True,
        ),
        _ActivityTestCase(
            name="no_start-past_end",
            start_type=None,
            end_type=_Time.PAST,
            expected_operational=False,
        ),
    ],
    ids=lambda case: case.name,
)
def test_active_property(
    past: datetime, future: datetime, now: datetime, case: _ActivityTestCase
) -> None:
    """Test the active property of Lifetime."""
    start_time = {
        _Time.PAST: past,
        _Time.FUTURE: future,
        _Time.NOW: now,
        None: None,
    }[case.start_type]

    end_time = {
        _Time.PAST: past,
        _Time.FUTURE: future,
        _Time.NOW: now,
        None: None,
    }[case.end_type]

    lifetime = Lifetime(start=start_time, end=end_time)
    assert lifetime.is_operational_at(now) == case.expected_operational


@pytest.mark.parametrize(
    "case",
    [
        _FixedLifetimeTestCase(
            name="past", test_time=_Time.PAST, expected_operational=True
        ),
        _FixedLifetimeTestCase(
            name="now", test_time=_Time.NOW, expected_operational=True
        ),
        _FixedLifetimeTestCase(
            name="future", test_time=_Time.FUTURE, expected_operational=True
        ),
    ],
    ids=lambda case: case.name,
)
def test_active_at_with_fixed_lifetime(
    past: datetime,
    future: datetime,
    now: datetime,
    case: _FixedLifetimeTestCase,
) -> None:
    """Test active_at with different timestamps for a fixed lifetime period."""
    lifetime = Lifetime(start=past, end=future)
    test_time = {
        _Time.PAST: past,
        _Time.NOW: now,
        _Time.FUTURE: future,
    }[case.test_time]

    assert lifetime.is_operational_at(test_time) == case.expected_operational


@pytest.mark.parametrize(
    "case",
    [
        _ProtoConversionTestCase(
            name="both timestamps", include_start=True, include_end=True
        ),
        _ProtoConversionTestCase(
            name="only start timestamp", include_start=True, include_end=False
        ),
        _ProtoConversionTestCase(
            name="only end timestamp", include_start=False, include_end=True
        ),
        _ProtoConversionTestCase(
            name="no timestamps", include_start=False, include_end=False
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(
    now: datetime, future: datetime, case: _ProtoConversionTestCase
) -> None:
    """Test conversion from protobuf message to Lifetime."""
    now_ts = timestamp_pb2.Timestamp()
    now_ts.FromDatetime(now)

    future_ts = timestamp_pb2.Timestamp()
    future_ts.FromDatetime(future)

    proto_kwargs: dict[str, Any] = {}
    if case.include_start:
        proto_kwargs["start_timestamp"] = now_ts
    if case.include_end:
        proto_kwargs["end_timestamp"] = future_ts

    proto = lifetime_pb2.Lifetime(**proto_kwargs)
    lifetime = lifetime_from_proto(proto)

    if case.include_start:
        assert lifetime.start == now
    else:
        assert lifetime.start is None

    if case.include_end:
        assert lifetime.end == future
    else:
        assert lifetime.end is None
