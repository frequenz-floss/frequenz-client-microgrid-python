# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for ProblematicComponent components."""

import pytest
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    ComponentCategory,
    MismatchedCategoryComponent,
    ProblematicComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)


@pytest.fixture
def component_id() -> ComponentId:
    """Provide a test component ID."""
    return ComponentId(42)


@pytest.fixture
def microgrid_id() -> MicrogridId:
    """Provide a test microgrid ID."""
    return MicrogridId(1)


def test_abstract_problematic_component_cannot_be_instantiated(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test that ProblematicComponent base class cannot be instantiated."""
    with pytest.raises(
        TypeError, match="Cannot instantiate ProblematicComponent directly"
    ):
        ProblematicComponent(
            id=component_id,
            microgrid_id=microgrid_id,
            name="test_problematic",
            manufacturer="test_manufacturer",
            model_name="test_model",
            category=ComponentCategory.UNSPECIFIED,
        )


def test_unspecified_component(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of UnspecifiedComponent."""
    component = UnspecifiedComponent(
        id=component_id,
        microgrid_id=microgrid_id,
        name="unspecified_component",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "unspecified_component"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == ComponentCategory.UNSPECIFIED


def test_mismatched_category_component_with_known_category(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test MismatchedCategoryComponent with a known ComponentCategory."""
    expected_category = ComponentCategory.BATTERY
    component = MismatchedCategoryComponent(
        id=component_id,
        microgrid_id=microgrid_id,
        name="mismatched_battery",
        manufacturer="test_manufacturer",
        model_name="test_model",
        category=expected_category,
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "mismatched_battery"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == expected_category


def test_mismatched_category_component_with_unrecognized_category(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test MismatchedCategoryComponent with an unrecognized integer category."""
    expected_category = 999
    component = MismatchedCategoryComponent(
        id=component_id,
        microgrid_id=microgrid_id,
        name="mismatched_unrecognized",
        manufacturer="test_manufacturer",
        model_name="test_model",
        category=expected_category,
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "mismatched_unrecognized"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == expected_category


def test_unrecognized_component_type(
    component_id: ComponentId, microgrid_id: MicrogridId
) -> None:
    """Test initialization and properties of UnrecognizedComponent type."""
    component = UnrecognizedComponent(
        id=component_id,
        microgrid_id=microgrid_id,
        name="unrecognized_component",
        manufacturer="test_manufacturer",
        model_name="test_model",
        category=999,
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "unrecognized_component"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == 999
