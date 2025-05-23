# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Converter component."""

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    ComponentCategory,
    ComponentStatus,
    Converter,
)


def test_init() -> None:
    """Test Converter component initialization."""
    component_id = ComponentId(1)
    microgrid_id = MicrogridId(1)
    component = Converter(
        id=component_id,
        microgrid_id=microgrid_id,
        name="test_converter",
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "test_converter"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.status == ComponentStatus.ACTIVE
    assert component.category == ComponentCategory.CONVERTER
