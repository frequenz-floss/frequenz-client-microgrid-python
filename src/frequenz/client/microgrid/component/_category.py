# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""The component categories that can be used in a microgrid."""

import enum

from frequenz.api.common.v1.microgrid.components import components_pb2


@enum.unique
class ComponentCategory(enum.Enum):
    """The known categories of components that can be present in a microgrid."""

    UNSPECIFIED = components_pb2.COMPONENT_CATEGORY_UNSPECIFIED
    """The component category is unspecified, probably due to an error in the message."""

    GRID = components_pb2.COMPONENT_CATEGORY_GRID
    """The point where the local microgrid is connected to the grid."""

    METER = components_pb2.COMPONENT_CATEGORY_METER
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = components_pb2.COMPONENT_CATEGORY_INVERTER
    """An electricity generator, with batteries or solar energy."""

    CONVERTER = components_pb2.COMPONENT_CATEGORY_CONVERTER
    """A DC-DC converter."""

    BATTERY = components_pb2.COMPONENT_CATEGORY_BATTERY
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = components_pb2.COMPONENT_CATEGORY_EV_CHARGER
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = components_pb2.COMPONENT_CATEGORY_CRYPTO_MINER
    """A crypto miner."""

    ELECTROLYZER = components_pb2.COMPONENT_CATEGORY_ELECTROLYZER
    """An electrolyzer for converting water into hydrogen and oxygen."""

    CHP = components_pb2.COMPONENT_CATEGORY_CHP
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    RELAY = components_pb2.COMPONENT_CATEGORY_RELAY
    """A relay.

    Relays generally have two states: open (connected) and closed (disconnected).
    They are generally placed in front of a component, e.g., an inverter, to
    control whether the component is connected to the grid or not.
    """

    PRECHARGER = components_pb2.COMPONENT_CATEGORY_PRECHARGER
    """A precharge module.

    Precharging involves gradually ramping up the DC voltage to prevent any
    potential damage to sensitive electrical components like capacitors.

    While many inverters and batteries come equipped with in-built precharging
    mechanisms, some may lack this feature. In such cases, we need to use
    external precharging modules.
    """

    VOLTAGE_TRANSFORMER = components_pb2.COMPONENT_CATEGORY_VOLTAGE_TRANSFORMER
    """A voltage transformer.

    Voltage transformers are used to step up or step down the voltage, keeping
    the power somewhat constant by increasing or decreasing the current.  If voltage is
    stepped up, current is stepped down, and vice versa.

    Note:
        Voltage transformers have efficiency losses, so the output power is
        always less than the input power.
    """

    HVAC = components_pb2.COMPONENT_CATEGORY_HVAC
    """A Heating, Ventilation, and Air Conditioning (HVAC) system."""
