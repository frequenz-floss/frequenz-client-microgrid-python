# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for GridConnectionPoint component."""

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentCategory, GridConnectionPoint


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


@pytest.mark.parametrize("rated_fuse_current", [0, 50])
def test_creation_ok(
    component_id: ComponentId, microgrid_id: MicrogridId, rated_fuse_current: int
) -> None:
    """Test GridConnectionPoint initialization with different rated fuse currents."""
    grid_point = GridConnectionPoint(
        id=component_id,
        microgrid_id=microgrid_id,
        name="test_grid_point",
        manufacturer="test_manufacturer",
        model_name="test_model",
        rated_fuse_current=rated_fuse_current,
    )

    assert grid_point.id == component_id
    assert grid_point.microgrid_id == microgrid_id
    assert grid_point.name == "test_grid_point"
    assert grid_point.manufacturer == "test_manufacturer"
    assert grid_point.model_name == "test_model"
    assert grid_point.category == ComponentCategory.GRID_CONNECTION_POINT
    assert grid_point.rated_fuse_current == rated_fuse_current


def test_creation_invalid_rated_fuse_current(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test Fuse component initialization with invalid rated current."""
    with pytest.raises(
        ValueError, match="rated_fuse_current must be a positive integer, not -1"
    ):
        GridConnectionPoint(
            id=component_id,
            microgrid_id=microgrid_id,
            name="test_grid_point",
            manufacturer="test_manufacturer",
            model_name="test_model",
            rated_fuse_current=-1,
        )
