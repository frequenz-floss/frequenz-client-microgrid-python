# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for WindTurbine component."""


from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentCategory, WindTurbine


def test_init() -> None:
    """Test WindTurbine component initialization."""
    component_id = ComponentId(1)
    microgrid_id = MicrogridId(1)
    component = WindTurbine(
        id=component_id,
        microgrid_id=microgrid_id,
        name="wind_turbine_test",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "wind_turbine_test"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == ComponentCategory.WIND_TURBINE
