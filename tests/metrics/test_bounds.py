# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Bounds class."""

import re
from dataclasses import dataclass

import pytest
from frequenz.api.common.v1alpha8.metrics import bounds_pb2

from frequenz.client.microgrid.metrics import Bounds
from frequenz.client.microgrid.metrics._bounds_proto import bounds_from_proto


@dataclass(frozen=True, kw_only=True)
class ProtoConversionTestCase:
    """Test case for protobuf conversion."""

    name: str
    """Description of the test case."""

    has_lower: bool
    """Whether to include lower bound in the protobuf message."""

    has_upper: bool
    """Whether to include upper bound in the protobuf message."""

    lower: float | None
    """The lower bound value to set."""

    upper: float | None
    """The upper bound value to set."""


@pytest.mark.parametrize(
    "lower, upper",
    [
        (None, None),
        (10.0, None),
        (None, -10.0),
        (-10.0, 10.0),
        (10.0, 10.0),
        (-10.0, -10.0),
        (0.0, 10.0),
        (-10, 0.0),
        (0.0, 0.0),
    ],
)
def test_creation(lower: float, upper: float) -> None:
    """Test creation of Bounds with valid values."""
    bounds = Bounds(lower=lower, upper=upper)
    assert bounds.lower == lower
    assert bounds.upper == upper


def test_invalid_values() -> None:
    """Test that Bounds creation fails with invalid values."""
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Lower bound (10.0) must be less than or equal to upper bound (-10.0)"
        ),
    ):
        Bounds(lower=10.0, upper=-10.0)


def test_str_representation() -> None:
    """Test string representation of Bounds."""
    bounds = Bounds(lower=-10.0, upper=10.0)
    assert str(bounds) == "[-10.0, 10.0]"


def test_equality() -> None:
    """Test equality comparison of Bounds objects."""
    bounds1 = Bounds(lower=-10.0, upper=10.0)
    bounds2 = Bounds(lower=-10.0, upper=10.0)
    bounds3 = Bounds(lower=-5.0, upper=5.0)

    assert bounds1 == bounds2
    assert bounds1 != bounds3
    assert bounds2 != bounds3


def test_hash() -> None:
    """Test that Bounds objects can be used in sets and as dictionary keys."""
    bounds1 = Bounds(lower=-10.0, upper=10.0)
    bounds2 = Bounds(lower=-10.0, upper=10.0)
    bounds3 = Bounds(lower=-5.0, upper=5.0)

    bounds_set = {bounds1, bounds2, bounds3}
    assert len(bounds_set) == 2  # bounds1 and bounds2 are equal

    bounds_dict = {bounds1: "test1", bounds3: "test2"}
    assert len(bounds_dict) == 2


@pytest.mark.parametrize(
    "case",
    [
        ProtoConversionTestCase(
            name="full",
            has_lower=True,
            has_upper=True,
            lower=-10.0,
            upper=10.0,
        ),
        ProtoConversionTestCase(
            name="no_upper_bound",
            has_lower=True,
            has_upper=False,
            lower=-10.0,
            upper=None,
        ),
        ProtoConversionTestCase(
            name="no_lower_bound",
            has_lower=False,
            has_upper=True,
            lower=None,
            upper=10.0,
        ),
        ProtoConversionTestCase(
            name="no_both_bounds",
            has_lower=False,
            has_upper=False,
            lower=None,
            upper=None,
        ),
    ],
    ids=lambda case: case.name,
)
def test_from_proto(case: ProtoConversionTestCase) -> None:
    """Test conversion from protobuf message to Bounds."""
    proto = bounds_pb2.Bounds()
    if case.has_lower and case.lower is not None:
        proto.lower = case.lower
    if case.has_upper and case.upper is not None:
        proto.upper = case.upper

    bounds = bounds_from_proto(proto)

    assert bounds.lower == case.lower
    assert bounds.upper == case.upper
