# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""HVAC component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hvac(Component):
    """A heating, ventilation, and air conditioning (HVAC) component."""

    category: Literal[ComponentCategory.HVAC] = ComponentCategory.HVAC
    """The category of this component."""
