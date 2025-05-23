# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Relay component."""

import dataclasses
from typing import Literal

from ._category import ComponentCategory
from ._component import Component


@dataclasses.dataclass(frozen=True, kw_only=True)
class Relay(Component):
    """A relay component."""

    category: Literal[ComponentCategory.RELAY] = ComponentCategory.RELAY
    """The category of this component."""
