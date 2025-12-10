# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Wind turbine component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class WindTurbine(Component):
    """A wind turbine component."""

    category: Literal[ComponentCategory.WIND_TURBINE] = ComponentCategory.WIND_TURBINE
    """The category of this component."""
