# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Fuse component."""

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentCategory, ComponentStatus, Fuse


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


@pytest.mark.parametrize("rated_current", [0, 50])
def test_creation_ok(
    component_id: ComponentId, microgrid_id: MicrogridId, rated_current: int
) -> None:
    """Test Fuse component initialization with different rated currents."""
    fuse = Fuse(
        id=component_id,
        microgrid_id=microgrid_id,
        name="test_fuse",
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
        rated_current=rated_current,
    )

    assert fuse.id == component_id
    assert fuse.microgrid_id == microgrid_id
    assert fuse.name == "test_fuse"
    assert fuse.manufacturer == "test_manufacturer"
    assert fuse.model_name == "test_model"
    assert fuse.status == ComponentStatus.ACTIVE
    assert fuse.category == ComponentCategory.FUSE
    assert fuse.rated_current == rated_current


def test_creation_invalid_rated_current(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test Fuse component initialization with invalid rated current."""
    with pytest.raises(
        ValueError, match="rated_current must be a positive integer, not -1"
    ):
        Fuse(
            id=component_id,
            microgrid_id=microgrid_id,
            name="test_fuse",
            manufacturer="test_manufacturer",
            model_name="test_model",
            status=ComponentStatus.ACTIVE,
            rated_current=-1,
        )
