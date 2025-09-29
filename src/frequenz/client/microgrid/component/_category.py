# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""The component categories that can be used in a microgrid."""

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.core import enum


@enum.unique
class ComponentCategory(enum.Enum):
    """The known categories of components that can be present in a microgrid."""

    UNSPECIFIED = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED
    """The component category is unspecified, probably due to an error in the message."""

    GRID_CONNECTION_POINT = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT
    )
    """The point where the local microgrid is connected to the grid."""

    GRID = enum.deprecated_member(
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT,
        "GRID is deprecated, use GRID_CONNECTION_POINT instead",
    )
    """The point where the local microgrid is connected to the grid (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use
        [`GRID_CONNECTION_POINT`][frequenz.client.microgrid.component.ComponentCategory.GRID_CONNECTION_POINT]
        instead.
    """

    METER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER
    """An electricity generator, with batteries or solar energy."""

    CONVERTER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER
    """A DC-DC converter."""

    BATTERY = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER
    """A crypto miner."""

    ELECTROLYZER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER
    """An electrolyzer for converting water into hydrogen and oxygen."""

    CHP = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    RELAY = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER
    """A relay.

    Relays generally have two states: open (connected) and closed (disconnected).
    They are generally placed in front of a component, e.g., an inverter, to
    control whether the component is connected to the grid or not.
    """

    PRECHARGER = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER
    """A precharge module.

    Precharging involves gradually ramping up the DC voltage to prevent any
    potential damage to sensitive electrical components like capacitors.

    While many inverters and batteries come equipped with in-built precharging
    mechanisms, some may lack this feature. In such cases, we need to use
    external precharging modules.
    """

    POWER_TRANSFORMER = (
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER
    )
    """A power transformer.

    A power transformer is designed for the bulk transfer of electrical energy. Its main
    job is to "step-up" or "step-down" voltage levels for efficient transmission and
    distribution of power.

    Since power transformers try to keep the output power same as the input
    power (ignoring losses), when they step-up the voltage, the current gets
    proportionally reduced, and vice versa.
    """

    VOLTAGE_TRANSFORMER = enum.deprecated_member(
        electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER,
        "VOLTAGE_TRANSFORMER is deprecated, use POWER_TRANSFORMER instead",
    )
    """A voltage transformer (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use
        [`POWER_TRANSFORMER`][frequenz.client.microgrid.component.ComponentCategory.POWER_TRANSFORMER]
        instead.
    """

    HVAC = electrical_components_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC
    """A Heating, Ventilation, and Air Conditioning (HVAC) system."""
