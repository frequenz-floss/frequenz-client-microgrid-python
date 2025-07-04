# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for CHP component."""


from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import Chp, ComponentCategory, ComponentStatus


def test_init() -> None:
    """Test CHP component initialization."""
    component_id = ComponentId(1)
    microgrid_id = MicrogridId(1)
    component = Chp(
        id=component_id,
        microgrid_id=microgrid_id,
        name="chp_test",
        manufacturer="test_manufacturer",
        model_name="test_model",
        status=ComponentStatus.ACTIVE,
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "chp_test"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.status == ComponentStatus.ACTIVE
    assert component.category == ComponentCategory.CHP
