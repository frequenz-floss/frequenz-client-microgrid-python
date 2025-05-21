# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the Component base class and its functionality."""

from datetime import datetime, timezone
from typing import Literal
from unittest.mock import Mock, patch

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid import Lifetime
from frequenz.client.microgrid.component._category import ComponentCategory
from frequenz.client.microgrid.component._component import Component
from frequenz.client.microgrid.component._status import ComponentStatus
from frequenz.client.microgrid.metrics._bounds import Bounds
from frequenz.client.microgrid.metrics._metric import Metric


class _TestComponent(Component):
    """A simple component implementation for testing."""

    category: Literal[ComponentCategory.UNSPECIFIED] = ComponentCategory.UNSPECIFIED


def test_base_creation_fails() -> None:
    """Test that Component base class cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Cannot instantiate Component directly"):
        _ = Component(
            id=ComponentId(1),
            microgrid_id=MicrogridId(1),
            category=ComponentCategory.UNSPECIFIED,
        )


def test_creation_with_defaults() -> None:
    """Test component default values."""
    component = _TestComponent(
        id=ComponentId(1),
        microgrid_id=MicrogridId(2),
        category=ComponentCategory.UNSPECIFIED,
    )

    assert component.status == ComponentStatus.UNSPECIFIED
    assert component.name is None
    assert component.manufacturer is None
    assert component.model_name is None
    assert component.operational_lifetime == Lifetime()
    assert component.rated_bounds == {}
    assert component.category_specific_metadata == {}


def test_creation_full() -> None:
    """Test component creation with all attributes."""
    bounds = Bounds(lower=-100.0, upper=100.0)
    rated_bounds: dict[Metric | int, Bounds] = {Metric.AC_ACTIVE_POWER: bounds}
    metadata = {"key1": "value1", "key2": 42}

    component = _TestComponent(
        id=ComponentId(1),
        microgrid_id=MicrogridId(2),
        category=ComponentCategory.UNSPECIFIED,
        name="test-component",
        manufacturer="Test Manufacturer",
        model_name="Test Model",
        rated_bounds=rated_bounds,
        category_specific_metadata=metadata,
    )

    assert component.name == "test-component"
    assert component.manufacturer == "Test Manufacturer"
    assert component.model_name == "Test Model"
    assert component.rated_bounds == rated_bounds
    assert component.category_specific_metadata == metadata


@pytest.mark.parametrize(
    "name,expected_str",
    [
        (None, "CID1<_TestComponent>"),
        ("test-component", "CID1<_TestComponent>:test-component"),
    ],
    ids=["no-name", "with-name"],
)
def test_str(name: str | None, expected_str: str) -> None:
    """Test string representation of a component."""
    component = _TestComponent(
        id=ComponentId(1),
        microgrid_id=MicrogridId(2),
        category=ComponentCategory.UNSPECIFIED,
        name=name,
    )
    assert str(component) == expected_str


@pytest.mark.parametrize("status", list(ComponentStatus), ids=lambda s: s.name)
@pytest.mark.parametrize(
    "lifetime_active", [True, False], ids=["operational", "not-operational"]
)
def test_active_at(
    status: ComponentStatus, lifetime_active: bool, caplog: pytest.LogCaptureFixture
) -> None:
    """Test active_at behavior with different status and lifetime combinations."""
    caplog.set_level("WARNING")

    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.is_operational_at.return_value = lifetime_active

    component = _TestComponent(
        id=ComponentId(1),
        microgrid_id=MicrogridId(1),
        category=ComponentCategory.UNSPECIFIED,
        status=status,
        operational_lifetime=mock_lifetime,
    )

    test_time = datetime.now(timezone.utc)
    expected = status != ComponentStatus.INACTIVE and lifetime_active
    assert component.is_active_at(test_time) == expected

    if status in (ComponentStatus.ACTIVE, ComponentStatus.UNSPECIFIED):
        mock_lifetime.is_operational_at.assert_called_once_with(test_time)
    else:
        mock_lifetime.is_operational_at.assert_not_called()

    if status is ComponentStatus.UNSPECIFIED:
        assert "unspecified status" in caplog.text.lower()


@patch("frequenz.client.microgrid.component._component.datetime")
def test_is_active_now(mock_datetime: Mock) -> None:
    """Test is_active_now method."""
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_datetime.now.side_effect = lambda tz: now.replace(tzinfo=tz)
    mock_lifetime = Mock(spec=Lifetime)
    mock_lifetime.is_operational_at.return_value = True
    component = _TestComponent(
        id=ComponentId(1),
        microgrid_id=MicrogridId(1),
        category=ComponentCategory.UNSPECIFIED,
        status=ComponentStatus.ACTIVE,
        operational_lifetime=mock_lifetime,
    )

    assert component.is_active_now() is True

    mock_lifetime.is_operational_at.assert_called_once_with(now)


COMPONENT = _TestComponent(
    id=ComponentId(1),
    microgrid_id=MicrogridId(1),
    category=ComponentCategory.UNSPECIFIED,
    status=ComponentStatus.ACTIVE,
    name="test",
    manufacturer="Test Mfg",
    model_name="Model A",
    rated_bounds={Metric.AC_ACTIVE_POWER: Bounds(lower=-100.0, upper=100.0)},
    category_specific_metadata={"key": "value"},
)

DIFFERENT_NONHASHABLE = _TestComponent(
    id=COMPONENT.id,
    microgrid_id=COMPONENT.microgrid_id,
    category=COMPONENT.category,
    status=COMPONENT.status,
    name=COMPONENT.name,
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds={Metric.AC_ACTIVE_POWER: Bounds(lower=-200.0, upper=200.0)},
    category_specific_metadata={"different": "metadata"},
)

DIFFERENT_STATUS = _TestComponent(
    id=COMPONENT.id,
    microgrid_id=COMPONENT.microgrid_id,
    category=COMPONENT.category,
    status=ComponentStatus.INACTIVE,
    name=COMPONENT.name,
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds=COMPONENT.rated_bounds,
    category_specific_metadata=COMPONENT.category_specific_metadata,
)

DIFFERENT_NAME = _TestComponent(
    id=COMPONENT.id,
    microgrid_id=COMPONENT.microgrid_id,
    category=COMPONENT.category,
    status=COMPONENT.status,
    name="different",
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds=COMPONENT.rated_bounds,
    category_specific_metadata=COMPONENT.category_specific_metadata,
)

DIFFERENT_ID = _TestComponent(
    id=ComponentId(2),
    microgrid_id=COMPONENT.microgrid_id,
    category=COMPONENT.category,
    status=COMPONENT.status,
    name=COMPONENT.name,
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds=COMPONENT.rated_bounds,
    category_specific_metadata=COMPONENT.category_specific_metadata,
)

DIFFERENT_MICROGRID_ID = _TestComponent(
    id=COMPONENT.id,
    microgrid_id=MicrogridId(2),
    category=COMPONENT.category,
    status=COMPONENT.status,
    name=COMPONENT.name,
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds=COMPONENT.rated_bounds,
    category_specific_metadata=COMPONENT.category_specific_metadata,
)

DIFFERENT_BOTH_ID = _TestComponent(
    id=ComponentId(2),
    microgrid_id=MicrogridId(2),
    category=COMPONENT.category,
    status=COMPONENT.status,
    name=COMPONENT.name,
    manufacturer=COMPONENT.manufacturer,
    model_name=COMPONENT.model_name,
    rated_bounds=COMPONENT.rated_bounds,
    category_specific_metadata=COMPONENT.category_specific_metadata,
)


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(COMPONENT, True, id="self"),
        pytest.param(DIFFERENT_NONHASHABLE, False, id="other-nonhashable"),
        pytest.param(DIFFERENT_STATUS, False, id="other-status"),
        pytest.param(DIFFERENT_NAME, False, id="other-name"),
        pytest.param(DIFFERENT_ID, False, id="other-id"),
        pytest.param(DIFFERENT_MICROGRID_ID, False, id="other-microgrid-id"),
        pytest.param(DIFFERENT_BOTH_ID, False, id="other-both-ids"),
    ],
    ids=lambda o: str(o.id) if isinstance(o, Component) else str(o),
)
def test_equality(comp: Component, expected: bool) -> None:
    """Test component equality."""
    assert (COMPONENT == comp) is expected
    assert (comp == COMPONENT) is expected
    assert (COMPONENT != comp) is not expected
    assert (comp != COMPONENT) is not expected


@pytest.mark.parametrize(
    "comp,expected",
    [
        pytest.param(COMPONENT, True, id="self"),
        pytest.param(DIFFERENT_NONHASHABLE, True, id="other-nonhashable"),
        pytest.param(DIFFERENT_STATUS, True, id="other-status"),
        pytest.param(DIFFERENT_NAME, True, id="other-name"),
        pytest.param(DIFFERENT_ID, False, id="other-id"),
        pytest.param(DIFFERENT_MICROGRID_ID, False, id="other-microgrid-id"),
        pytest.param(DIFFERENT_BOTH_ID, False, id="other-both-ids"),
    ],
)
def test_identity(comp: Component, expected: bool) -> None:
    """Test component identity."""
    assert (COMPONENT.identity == comp.identity) is expected
    assert comp.identity == (comp.id, comp.microgrid_id)


ALL_COMPONENTS_PARAMS = [
    pytest.param(COMPONENT, id="comp"),
    pytest.param(DIFFERENT_NONHASHABLE, id="nonhashable"),
    pytest.param(DIFFERENT_STATUS, id="status"),
    pytest.param(DIFFERENT_NAME, id="name"),
    pytest.param(DIFFERENT_ID, id="id"),
    pytest.param(DIFFERENT_MICROGRID_ID, id="microgrid_id"),
    pytest.param(DIFFERENT_BOTH_ID, id="both_ids"),
]


@pytest.mark.parametrize("comp1", ALL_COMPONENTS_PARAMS)
@pytest.mark.parametrize("comp2", ALL_COMPONENTS_PARAMS)
def test_hash(comp1: Component, comp2: Component) -> None:
    """Test that the hash is consistent."""
    # We can only say the hash are the same if the components are equal, if they
    # are not, they could still have the same hash (and they will if they have
    # only different non-hashable attributes)
    if comp1 == comp2:
        assert hash(comp1) == hash(comp2)
