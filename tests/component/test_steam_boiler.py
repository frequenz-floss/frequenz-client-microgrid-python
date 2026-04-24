# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for steam boiler component."""

from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import ComponentCategory, SteamBoiler


def test_init() -> None:
    """Test steam boiler component initialization."""
    component_id = ComponentId(1)
    microgrid_id = MicrogridId(1)
    component = SteamBoiler(
        id=component_id,
        microgrid_id=microgrid_id,
        name="test_steam_boiler",
        manufacturer="test_manufacturer",
        model_name="test_model",
    )

    assert component.id == component_id
    assert component.microgrid_id == microgrid_id
    assert component.name == "test_steam_boiler"
    assert component.manufacturer == "test_manufacturer"
    assert component.model_name == "test_model"
    assert component.category == ComponentCategory.STEAM_BOILER
