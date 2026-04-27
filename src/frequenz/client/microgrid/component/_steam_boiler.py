# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Steam boiler component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class SteamBoiler(Component):
    """A steam boiler component."""

    category: Literal[ComponentCategory.STEAM_BOILER] = ComponentCategory.STEAM_BOILER
    """The category of this component."""
