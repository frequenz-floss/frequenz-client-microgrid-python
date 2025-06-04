# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the ComponentStateSample class and proto conversion."""

from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from frequenz.api.common.v1.microgrid.components import components_pb2
from frequenz.client.base.conversion import to_timestamp

from frequenz.client.microgrid.component import (
    ComponentErrorCode,
    ComponentStateCode,
    ComponentStateSample,
)
from frequenz.client.microgrid.component._state_sample_proto import (
    component_state_sample_from_proto,
)


@pytest.fixture
def timestamp() -> datetime:
    """Provide a fixed timestamp for testing."""
    return datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_init(timestamp: datetime) -> None:
    """Test initialization of ComponentStateSample."""
    states = frozenset([ComponentStateCode.READY])
    warnings = frozenset([ComponentErrorCode.HARDWARE_INACCESSIBLE])
    errors: frozenset[ComponentErrorCode] = frozenset()

    state_sample = ComponentStateSample(
        sampled_at=timestamp,
        states=states,
        warnings=warnings,
        errors=errors,
    )

    assert state_sample.sampled_at == timestamp
    assert state_sample.states == states
    assert state_sample.warnings == warnings
    assert state_sample.errors == errors


def test_equality(timestamp: datetime) -> None:
    """Test equality of ComponentStateSample instances."""
    states1 = frozenset([ComponentStateCode.READY])
    warnings1 = frozenset([ComponentErrorCode.HARDWARE_INACCESSIBLE])
    errors1: frozenset[ComponentErrorCode] = frozenset()

    state_sample1 = ComponentStateSample(
        sampled_at=timestamp,
        states=states1,
        warnings=warnings1,
        errors=errors1,
    )

    state_sample2 = ComponentStateSample(
        sampled_at=timestamp,
        states=states1,
        warnings=warnings1,
        errors=errors1,
    )

    different_timestamp = ComponentStateSample(
        sampled_at=datetime(2025, 3, 1, 13, 0, 0, tzinfo=timezone.utc),
        states=states1,
        warnings=warnings1,
        errors=errors1,
    )

    different_states = ComponentStateSample(
        sampled_at=timestamp,
        states=frozenset([ComponentStateCode.ERROR]),
        warnings=warnings1,
        errors=errors1,
    )

    different_warnings = ComponentStateSample(
        sampled_at=timestamp,
        states=states1,
        warnings=frozenset(),
        errors=errors1,
    )

    different_errors = ComponentStateSample(
        sampled_at=timestamp,
        states=frozenset([ComponentStateCode.ERROR]),
        warnings=warnings1,
        errors=frozenset([ComponentErrorCode.OVERCURRENT]),
    )

    assert state_sample1 == state_sample2
    assert state_sample1 != different_timestamp
    assert state_sample1 != different_states
    assert state_sample1 != different_warnings
    assert state_sample1 != different_errors


@dataclass(frozen=True, kw_only=True)
class ProtoConversionCase:
    """Test case for proto conversion tests."""

    name: str
    states: list[ComponentStateCode | int]
    warnings: list[ComponentErrorCode | int]
    errors: list[ComponentErrorCode | int]


@pytest.mark.parametrize(
    "case",
    [
        ProtoConversionCase(
            name="full",
            states=[ComponentStateCode.ERROR],
            warnings=[ComponentErrorCode.HARDWARE_INACCESSIBLE],
            errors=[ComponentErrorCode.OVERCURRENT],
        ),
        ProtoConversionCase(
            name="empty",
            states=[],
            warnings=[],
            errors=[],
        ),
        ProtoConversionCase(
            name="only_states",
            states=[ComponentStateCode.READY, ComponentStateCode.STANDBY],
            warnings=[],
            errors=[],
        ),
        ProtoConversionCase(
            name="only_warnings",
            states=[],
            warnings=[ComponentErrorCode.HARDWARE_INACCESSIBLE],
            errors=[],
        ),
        ProtoConversionCase(
            name="only_errors",
            states=[],
            warnings=[],
            errors=[ComponentErrorCode.OVERCURRENT],
        ),
        ProtoConversionCase(
            name="unknown_codes",
            states=[9999],
            warnings=[8888],
            errors=[7777],
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(
    case: ProtoConversionCase,
    timestamp: datetime,
) -> None:
    """Test conversion from proto message to ComponentStateSample."""
    proto = components_pb2.ComponentState(
        sampled_at=to_timestamp(timestamp),
        states=(
            state.value if isinstance(state, ComponentStateCode) else state  # type: ignore[misc]
            for state in case.states
        ),
        warnings=(
            (
                warning.value  # type: ignore[misc]
                if isinstance(warning, ComponentErrorCode)
                else warning
            )
            for warning in case.warnings
        ),
        errors=(
            error.value if isinstance(error, ComponentErrorCode) else error  # type: ignore[misc]
            for error in case.errors
        ),
    )

    with patch("frequenz.client.base.conversion.to_datetime", return_value=timestamp):
        result = component_state_sample_from_proto(proto)

    assert result.sampled_at == timestamp
    assert result.states == frozenset(case.states)
    assert result.warnings == frozenset(case.warnings)
    assert result.errors == frozenset(case.errors)
