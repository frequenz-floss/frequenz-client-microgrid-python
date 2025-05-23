# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with various component types."""

from typing import Any

from frequenz.api.common.v1.microgrid.components import (
    battery_pb2,
    components_pb2,
    ev_charger_pb2,
    fuse_pb2,
    grid_pb2,
    inverter_pb2,
)
from frequenz.api.microgrid.v1 import microgrid_pb2
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId

from frequenz.client.microgrid.component import (
    AcEvCharger,
    Battery,
    BatteryInverter,
    BatteryType,
    Chp,
    ComponentCategory,
    Converter,
    CryptoMiner,
    DcEvCharger,
    Electrolyzer,
    EvCharger,
    EvChargerType,
    Fuse,
    GridConnectionPoint,
    Hvac,
    HybridEvCharger,
    HybridInverter,
    Inverter,
    InverterType,
    LiIonBattery,
    Meter,
    MismatchedCategoryComponent,
    NaIonBattery,
    Precharger,
    Relay,
    SolarInverter,
    UnrecognizedBattery,
    UnrecognizedComponent,
    UnrecognizedEvCharger,
    UnrecognizedInverter,
    UnspecifiedBattery,
    UnspecifiedComponent,
    UnspecifiedEvCharger,
    UnspecifiedInverter,
    VoltageTransformer,
)

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListComponentsRequest(component_ids=[], categories=[]),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListComponentsResponse(
    components=[
        components_pb2.Component(
            id=1,
            microgrid_id=1,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_GRID,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                grid=grid_pb2.GridConnectionPoint(rated_fuse_current=10_000)
            ),
        ),
        components_pb2.Component(
            id=2,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_SOLAR
                )
            ),
        ),
        components_pb2.Component(
            id=3,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                battery=battery_pb2.Battery(
                    type=battery_pb2.BatteryType.BATTERY_TYPE_LI_ION
                )
            ),
        ),
        components_pb2.Component(
            id=4, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_CONVERTER
        ),
        components_pb2.Component(
            id=5, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_METER
        ),
        components_pb2.Component(
            id=6,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                ev_charger=ev_charger_pb2.EvCharger(
                    type=ev_charger_pb2.EvChargerType.EV_CHARGER_TYPE_AC
                )
            ),
        ),
        components_pb2.Component(
            id=7,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_FUSE,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                fuse=fuse_pb2.Fuse(rated_current=50)
            ),
        ),
        components_pb2.Component(
            id=8, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_HVAC
        ),
        # Additional battery types
        components_pb2.Component(
            id=9,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                battery=battery_pb2.Battery(
                    type=battery_pb2.BatteryType.BATTERY_TYPE_UNSPECIFIED
                )
            ),
        ),
        components_pb2.Component(
            id=10,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                battery=battery_pb2.Battery(
                    type=battery_pb2.BatteryType.BATTERY_TYPE_NA_ION
                )
            ),
        ),
        components_pb2.Component(
            id=11,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                battery=battery_pb2.Battery(
                    type=666,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional inverter types
        components_pb2.Component(
            id=12,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_UNSPECIFIED
                )
            ),
        ),
        components_pb2.Component(
            id=13,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_BATTERY
                )
            ),
        ),
        components_pb2.Component(
            id=14,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_HYBRID
                )
            ),
        ),
        components_pb2.Component(
            id=15,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_INVERTER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                inverter=inverter_pb2.Inverter(
                    type=777,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional EV charger types
        components_pb2.Component(
            id=16,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                ev_charger=ev_charger_pb2.EvCharger(
                    type=ev_charger_pb2.EvChargerType.EV_CHARGER_TYPE_UNSPECIFIED
                )
            ),
        ),
        components_pb2.Component(
            id=17,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                ev_charger=ev_charger_pb2.EvCharger(
                    type=ev_charger_pb2.EvChargerType.EV_CHARGER_TYPE_DC
                )
            ),
        ),
        components_pb2.Component(
            id=18,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                ev_charger=ev_charger_pb2.EvCharger(
                    type=ev_charger_pb2.EvChargerType.EV_CHARGER_TYPE_HYBRID
                )
            ),
        ),
        components_pb2.Component(
            id=19,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_EV_CHARGER,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                ev_charger=ev_charger_pb2.EvCharger(
                    type=888,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional component categories
        components_pb2.Component(
            id=20, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_CHP
        ),
        components_pb2.Component(
            id=21,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_CRYPTO_MINER,
        ),
        components_pb2.Component(
            id=22,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_ELECTROLYZER,
        ),
        components_pb2.Component(
            id=23,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_PRECHARGER,
        ),
        components_pb2.Component(
            id=24, category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_RELAY
        ),
        components_pb2.Component(
            id=25,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_VOLTAGE_TRANSFORMER,
        ),
        # Problematic components
        components_pb2.Component(
            id=26,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED,
        ),
        components_pb2.Component(
            id=27,
            category=999,  # type: ignore[arg-type]
        ),
        components_pb2.Component(
            id=28,
            category=components_pb2.ComponentCategory.COMPONENT_CATEGORY_BATTERY,
            category_type=components_pb2.ComponentCategoryMetadataVariant(
                # Mismatched: battery category with inverter metadata
                inverter=inverter_pb2.Inverter(
                    type=inverter_pb2.InverterType.INVERTER_TYPE_SOLAR
                )
            ),
        ),
    ]
)


def assert_client_result(result: Any) -> None:
    """Assert that the client result matches the expected components."""
    components = list(result)
    assert components == [
        GridConnectionPoint(
            id=ComponentId(1), microgrid_id=MicrogridId(1), rated_fuse_current=10_000
        ),
        SolarInverter(id=ComponentId(2), microgrid_id=MicrogridId(0)),
        LiIonBattery(id=ComponentId(3), microgrid_id=MicrogridId(0)),
        Converter(id=ComponentId(4), microgrid_id=MicrogridId(0)),
        Meter(id=ComponentId(5), microgrid_id=MicrogridId(0)),
        AcEvCharger(id=ComponentId(6), microgrid_id=MicrogridId(0)),
        Fuse(id=ComponentId(7), microgrid_id=MicrogridId(0), rated_current=50),
        Hvac(id=ComponentId(8), microgrid_id=MicrogridId(0)),
        # Additional battery types
        UnspecifiedBattery(id=ComponentId(9), microgrid_id=MicrogridId(0)),
        NaIonBattery(id=ComponentId(10), microgrid_id=MicrogridId(0)),
        UnrecognizedBattery(id=ComponentId(11), microgrid_id=MicrogridId(0), type=666),
        # Additional inverter types
        UnspecifiedInverter(id=ComponentId(12), microgrid_id=MicrogridId(0)),
        BatteryInverter(id=ComponentId(13), microgrid_id=MicrogridId(0)),
        HybridInverter(id=ComponentId(14), microgrid_id=MicrogridId(0)),
        UnrecognizedInverter(
            id=ComponentId(15), microgrid_id=MicrogridId(0), type=777
        ),  # Default type value
        # Additional EV charger types
        UnspecifiedEvCharger(id=ComponentId(16), microgrid_id=MicrogridId(0)),
        DcEvCharger(id=ComponentId(17), microgrid_id=MicrogridId(0)),
        HybridEvCharger(id=ComponentId(18), microgrid_id=MicrogridId(0)),
        UnrecognizedEvCharger(
            id=ComponentId(19), microgrid_id=MicrogridId(0), type=888
        ),  # Default type value
        # Additional component categories
        Chp(id=ComponentId(20), microgrid_id=MicrogridId(0)),
        CryptoMiner(id=ComponentId(21), microgrid_id=MicrogridId(0)),
        Electrolyzer(id=ComponentId(22), microgrid_id=MicrogridId(0)),
        Precharger(id=ComponentId(23), microgrid_id=MicrogridId(0)),
        Relay(id=ComponentId(24), microgrid_id=MicrogridId(0)),
        VoltageTransformer(
            id=ComponentId(25),
            microgrid_id=MicrogridId(0),
            primary_voltage=0.0,
            secondary_voltage=0.0,
        ),
        # Problematic components
        UnspecifiedComponent(id=ComponentId(26), microgrid_id=MicrogridId(0)),
        UnrecognizedComponent(
            id=ComponentId(27), microgrid_id=MicrogridId(0), category=999
        ),
        MismatchedCategoryComponent(
            id=ComponentId(28),
            microgrid_id=MicrogridId(0),
            category=ComponentCategory.BATTERY,
            category_specific_metadata={
                "type": "INVERTER_TYPE_SOLAR",
            },
        ),
    ]

    # Make sure we are testing all known categories and types
    assert set(ComponentCategory) == {
        component.category for component in components
    } - {999}
    assert set(BatteryType) == {
        battery.type for battery in components if isinstance(battery, Battery)
    } - {666}
    assert set(InverterType) == {
        inverter.type for inverter in components if isinstance(inverter, Inverter)
    } - {777}
    assert set(EvChargerType) == {
        ev_charger.type
        for ev_charger in components
        if isinstance(ev_charger, EvCharger)
    } - {888}
