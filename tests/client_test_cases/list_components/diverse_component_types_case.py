# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Test list_components with various component types."""

from typing import Any

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2 as ec_pb2,
)
from frequenz.api.microgrid.v1alpha18 import microgrid_pb2
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
    WindTurbine,
)

# No client_args or client_kwargs needed for this call


def assert_stub_method_call(stub_method: Any) -> None:
    """Assert that the gRPC request matches the expected request."""
    stub_method.assert_called_once_with(
        microgrid_pb2.ListElectricalComponentsRequest(
            electrical_component_ids=[], electrical_component_categories=[]
        ),
        timeout=60.0,
    )


grpc_response = microgrid_pb2.ListElectricalComponentsResponse(
    electrical_components=[
        ec_pb2.ElectricalComponent(
            id=1,
            microgrid_id=1,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                grid_connection_point=ec_pb2.GridConnectionPoint(
                    rated_fuse_current=10_000
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=2,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                inverter=ec_pb2.Inverter(type=ec_pb2.InverterType.INVERTER_TYPE_PV)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=3,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                battery=ec_pb2.Battery(type=ec_pb2.BatteryType.BATTERY_TYPE_LI_ION)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=4,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER,
        ),
        ec_pb2.ElectricalComponent(
            id=5,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_METER,
        ),
        ec_pb2.ElectricalComponent(
            id=6,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                ev_charger=ec_pb2.EvCharger(
                    type=ec_pb2.EvChargerType.EV_CHARGER_TYPE_AC
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=8,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_HVAC,
        ),
        # Additional battery types
        ec_pb2.ElectricalComponent(
            id=9,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                battery=ec_pb2.Battery(type=ec_pb2.BatteryType.BATTERY_TYPE_UNSPECIFIED)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=10,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                battery=ec_pb2.Battery(type=ec_pb2.BatteryType.BATTERY_TYPE_NA_ION)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=11,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                battery=ec_pb2.Battery(
                    type=666,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional inverter types
        ec_pb2.ElectricalComponent(
            id=12,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                inverter=ec_pb2.Inverter(
                    type=ec_pb2.InverterType.INVERTER_TYPE_UNSPECIFIED
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=13,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                inverter=ec_pb2.Inverter(type=ec_pb2.InverterType.INVERTER_TYPE_BATTERY)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=14,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                inverter=ec_pb2.Inverter(type=ec_pb2.InverterType.INVERTER_TYPE_HYBRID)
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=15,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_INVERTER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                inverter=ec_pb2.Inverter(
                    type=777,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional EV charger types
        ec_pb2.ElectricalComponent(
            id=16,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                ev_charger=ec_pb2.EvCharger(
                    type=ec_pb2.EvChargerType.EV_CHARGER_TYPE_UNSPECIFIED
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=17,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                ev_charger=ec_pb2.EvCharger(
                    type=ec_pb2.EvChargerType.EV_CHARGER_TYPE_DC
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=18,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                ev_charger=ec_pb2.EvCharger(
                    type=ec_pb2.EvChargerType.EV_CHARGER_TYPE_HYBRID
                )
            ),
        ),
        ec_pb2.ElectricalComponent(
            id=19,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                ev_charger=ec_pb2.EvCharger(
                    type=888,  # type: ignore[arg-type]
                )
            ),
        ),
        # Additional component categories
        ec_pb2.ElectricalComponent(
            id=20,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_CHP,
        ),
        ec_pb2.ElectricalComponent(
            id=21,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER,
        ),
        ec_pb2.ElectricalComponent(
            id=22,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER,
        ),
        ec_pb2.ElectricalComponent(
            id=23,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER,
        ),
        ec_pb2.ElectricalComponent(
            id=24,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BREAKER,
        ),
        ec_pb2.ElectricalComponent(
            id=25,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER,
        ),
        ec_pb2.ElectricalComponent(
            id=26,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_WIND_TURBINE,
        ),
        # Problematic components
        ec_pb2.ElectricalComponent(
            id=27,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED,
        ),
        ec_pb2.ElectricalComponent(
            id=28,
            category=999,  # type: ignore[arg-type]
        ),
        ec_pb2.ElectricalComponent(
            id=29,
            category=ec_pb2.ELECTRICAL_COMPONENT_CATEGORY_BATTERY,
            category_specific_info=ec_pb2.ElectricalComponentCategorySpecificInfo(
                # Mismatched: battery category with inverter metadata
                inverter=ec_pb2.Inverter(type=ec_pb2.InverterType.INVERTER_TYPE_PV)
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
        WindTurbine(id=ComponentId(26), microgrid_id=MicrogridId(0)),
        # Problematic components
        UnspecifiedComponent(id=ComponentId(27), microgrid_id=MicrogridId(0)),
        UnrecognizedComponent(
            id=ComponentId(28), microgrid_id=MicrogridId(0), category=999
        ),
        MismatchedCategoryComponent(
            id=ComponentId(29),
            microgrid_id=MicrogridId(0),
            category=ComponentCategory.BATTERY,
            category_specific_metadata={
                "type": "INVERTER_TYPE_PV",
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
