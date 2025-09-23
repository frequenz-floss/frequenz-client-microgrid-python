# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""All known component types."""

from typing import TypeAlias

from ._battery import BatteryTypes, UnrecognizedBattery, UnspecifiedBattery
from ._chp import Chp
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrolyzer import Electrolyzer
from ._ev_charger import EvChargerTypes, UnrecognizedEvCharger, UnspecifiedEvCharger
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import InverterTypes, UnrecognizedInverter, UnspecifiedInverter
from ._meter import Meter
from ._precharger import Precharger
from ._problematic import (
    MismatchedCategoryComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)
from ._relay import Relay
from ._voltage_transformer import VoltageTransformer

UnspecifiedComponentTypes: TypeAlias = (
    UnspecifiedBattery
    | UnspecifiedComponent
    | UnspecifiedEvCharger
    | UnspecifiedInverter
)
"""All unspecified component types."""

UnrecognizedComponentTypes: TypeAlias = (
    UnrecognizedBattery
    | UnrecognizedComponent
    | UnrecognizedEvCharger
    | UnrecognizedInverter
)

ProblematicComponentTypes: TypeAlias = (
    MismatchedCategoryComponent | UnrecognizedComponentTypes | UnspecifiedComponentTypes
)
"""All possible component types that has a problem."""

ComponentTypes: TypeAlias = (
    BatteryTypes
    | Chp
    | Converter
    | CryptoMiner
    | Electrolyzer
    | EvChargerTypes
    | GridConnectionPoint
    | Hvac
    | InverterTypes
    | Meter
    | Precharger
    | ProblematicComponentTypes
    | Relay
    | VoltageTransformer
)
"""All possible component types."""
