# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""CHP component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Chp(Component):
    """A combined heat and power (CHP) component."""

    category: Literal[ComponentCategory.CHP] = ComponentCategory.CHP
    """The category of this component."""
