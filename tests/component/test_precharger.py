# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for Precharger component."""


from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentCategory, Precharger


def test_init() -> None:
    """Test Precharger component initialization."""
    component_id = ComponentId(1)
    microgrid_id = MicrogridId(1)
    component = Precharger(
        id=component_id,
        microgrid_id=microgrid_id,
        name="precharger_test",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "precharger_test"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == ComponentCategory.PRECHARGER
