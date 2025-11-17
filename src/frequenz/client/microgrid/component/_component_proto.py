# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Loading of Component objects from protobuf messages."""

import logging
from collections.abc import Sequence
from typing import Any, NamedTuple, assert_never

from frequenz.api.common.v1alpha8.microgrid.electrical_components import (
    electrical_components_pb2,
)
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.components import ComponentId
from google.protobuf.json_format import MessageToDict

from .._lifetime import Lifetime
from .._lifetime_proto import lifetime_from_proto
from .._util import enum_from_proto
from ..metrics._bounds import Bounds
from ..metrics._bounds_proto import bounds_from_proto
from ..metrics._metric import Metric
from ._battery import (
    BatteryType,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)
from ._category import ComponentCategory
from ._chp import Chp
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrolyzer import Electrolyzer
from ._ev_charger import (
    AcEvCharger,
    DcEvCharger,
    EvChargerType,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import (
    BatteryInverter,
    HybridInverter,
    InverterType,
    SolarInverter,
    UnrecognizedInverter,
    UnspecifiedInverter,
)
from ._meter import Meter
from ._precharger import Precharger
from ._problematic import (
    MismatchedCategoryComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)
from ._relay import Relay
from ._types import ComponentTypes
from ._voltage_transformer import VoltageTransformer

_logger = logging.getLogger(__name__)


# We disable the `too-many-arguments` check in the whole file because all _from_proto
# functions are expected to take many arguments.
# pylint: disable=too-many-arguments


def component_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
) -> ComponentTypes:
    """Convert a protobuf message to a `Component` instance.

    Args:
        message: The protobuf message.

    Returns:
        The resulting `Component` instance.
    """
    major_issues: list[str] = []
    minor_issues: list[str] = []

    component = component_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if major_issues:
        _logger.warning(
            "Found issues in component: %s | Protobuf message:\n%s",
            ", ".join(major_issues),
            message,
        )
    if minor_issues:
        _logger.debug(
            "Found minor issues in component: %s | Protobuf message:\n%s",
            ", ".join(minor_issues),
            message,
        )

    return component


class ComponentBaseData(NamedTuple):
    """Base data for a component, extracted from a protobuf message."""

    component_id: ComponentId
    microgrid_id: MicrogridId
    name: str | None
    manufacturer: str | None
    model_name: str | None
    category: ComponentCategory | int
    lifetime: Lifetime
    rated_bounds: dict[Metric | int, Bounds]
    category_specific_info: dict[str, Any]
    category_mismatched: bool = False


def component_base_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ComponentBaseData:
    """Extract base data from a protobuf message and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        A `ComponentBaseData` named tuple containing the extracted data.
    """
    component_id = ComponentId(message.id)
    microgrid_id = MicrogridId(message.microgrid_id)

    name = message.name or None
    if name is None:
        minor_issues.append("name is empty")

    manufacturer = message.manufacturer or None
    if manufacturer is None:
        minor_issues.append("manufacturer is empty")

    model_name = message.model_name or None
    if model_name is None:
        minor_issues.append("model_name is empty")

    lifetime = _get_operational_lifetime_from_proto(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    rated_bounds = _metric_config_bounds_from_proto(
        message.metric_config_bounds,
        major_issues=major_issues,
        minor_issues=minor_issues,
    )

    category = enum_from_proto(message.category, ComponentCategory)
    if category is ComponentCategory.UNSPECIFIED:
        major_issues.append("category is unspecified")
    elif isinstance(category, int):
        major_issues.append(f"category {category} is unrecognized")

    category_specific_info_kind = message.category_specific_info.WhichOneof("kind")
    category_specific_info: dict[str, Any] = {}
    if category_specific_info_kind is not None:
        category_specific_info = MessageToDict(
            getattr(message.category_specific_info, category_specific_info_kind),
            always_print_fields_with_no_presence=True,
        )

    category_mismatched = False
    if (
        category_specific_info_kind
        and isinstance(category, ComponentCategory)
        and category.name.lower() != category_specific_info_kind
    ):
        major_issues.append(
            f"category_specific_info.kind ({category_specific_info_kind}) does not "
            f"match the category ({category.name.lower()})",
        )
        category_mismatched = True

    return ComponentBaseData(
        component_id,
        microgrid_id,
        name,
        manufacturer,
        model_name,
        category,
        lifetime,
        rated_bounds,
        category_specific_info,
        category_mismatched,
    )


# pylint: disable-next=too-many-locals, too-many-branches
def component_from_proto_with_issues(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> ComponentTypes:
    """Convert a protobuf message to a `Component` instance and collect issues.

    Args:
        message: The protobuf message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting `Component` instance.
    """
    base_data = component_base_from_proto_with_issues(
        message, major_issues=major_issues, minor_issues=minor_issues
    )

    if base_data.category_mismatched:
        return MismatchedCategoryComponent(
            id=base_data.component_id,
            microgrid_id=base_data.microgrid_id,
            name=base_data.name,
            manufacturer=base_data.manufacturer,
            model_name=base_data.model_name,
            category=base_data.category,
            operational_lifetime=base_data.lifetime,
            category_specific_metadata=base_data.category_specific_info,
            rated_bounds=base_data.rated_bounds,
        )

    match base_data.category:
        case int():
            return UnrecognizedComponent(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                category=base_data.category,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
            )
        case (
            ComponentCategory.UNSPECIFIED
            | ComponentCategory.CHP
            | ComponentCategory.CONVERTER
            | ComponentCategory.CRYPTO_MINER
            | ComponentCategory.ELECTROLYZER
            | ComponentCategory.HVAC
            | ComponentCategory.METER
            | ComponentCategory.PRECHARGER
            | ComponentCategory.RELAY
        ):
            return _trivial_category_to_class(base_data.category)(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
            )
        case ComponentCategory.BATTERY:
            battery_enum_to_class: dict[
                BatteryType, type[UnspecifiedBattery | LiIonBattery | NaIonBattery]
            ] = {
                BatteryType.UNSPECIFIED: UnspecifiedBattery,
                BatteryType.LI_ION: LiIonBattery,
                BatteryType.NA_ION: NaIonBattery,
            }
            battery_type = enum_from_proto(
                message.category_specific_info.battery.type, BatteryType
            )
            match battery_type:
                case BatteryType.UNSPECIFIED | BatteryType.LI_ION | BatteryType.NA_ION:
                    if battery_type is BatteryType.UNSPECIFIED:
                        major_issues.append("battery type is unspecified")
                    return battery_enum_to_class[battery_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(f"battery type {battery_type} is unrecognized")
                    return UnrecognizedBattery(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                        type=battery_type,
                    )
                case unexpected_battery_type:
                    assert_never(unexpected_battery_type)
        case ComponentCategory.EV_CHARGER:
            ev_charger_enum_to_class: dict[
                EvChargerType,
                type[
                    UnspecifiedEvCharger | AcEvCharger | DcEvCharger | HybridEvCharger
                ],
            ] = {
                EvChargerType.UNSPECIFIED: UnspecifiedEvCharger,
                EvChargerType.AC: AcEvCharger,
                EvChargerType.DC: DcEvCharger,
                EvChargerType.HYBRID: HybridEvCharger,
            }
            ev_charger_type = enum_from_proto(
                message.category_specific_info.ev_charger.type, EvChargerType
            )
            match ev_charger_type:
                case (
                    EvChargerType.UNSPECIFIED
                    | EvChargerType.AC
                    | EvChargerType.DC
                    | EvChargerType.HYBRID
                ):
                    if ev_charger_type is EvChargerType.UNSPECIFIED:
                        major_issues.append("ev_charger type is unspecified")
                    return ev_charger_enum_to_class[ev_charger_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(
                        f"ev_charger type {ev_charger_type} is unrecognized"
                    )
                    return UnrecognizedEvCharger(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                        type=ev_charger_type,
                    )
                case unexpected_ev_charger_type:
                    assert_never(unexpected_ev_charger_type)
        case ComponentCategory.GRID_CONNECTION_POINT | ComponentCategory.GRID:
            rated_fuse_current = (
                message.category_specific_info.grid_connection_point.rated_fuse_current
            )
            # No need to check for negatives because the protobuf type is uint32.
            return GridConnectionPoint(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
                rated_fuse_current=rated_fuse_current,
            )
        case ComponentCategory.INVERTER:
            inverter_enum_to_class: dict[
                InverterType,
                type[
                    UnspecifiedInverter
                    | BatteryInverter
                    | SolarInverter
                    | HybridInverter
                ],
            ] = {
                InverterType.UNSPECIFIED: UnspecifiedInverter,
                InverterType.BATTERY: BatteryInverter,
                InverterType.SOLAR: SolarInverter,
                InverterType.HYBRID: HybridInverter,
            }
            inverter_type = enum_from_proto(
                message.category_specific_info.inverter.type, InverterType
            )
            match inverter_type:
                case (
                    InverterType.UNSPECIFIED
                    | InverterType.BATTERY
                    | InverterType.SOLAR
                    | InverterType.HYBRID
                ):
                    if inverter_type is InverterType.UNSPECIFIED:
                        major_issues.append("inverter type is unspecified")
                    return inverter_enum_to_class[inverter_type](
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                    )
                case int():
                    major_issues.append(
                        f"inverter type {inverter_type} is unrecognized"
                    )
                    return UnrecognizedInverter(
                        id=base_data.component_id,
                        microgrid_id=base_data.microgrid_id,
                        name=base_data.name,
                        manufacturer=base_data.manufacturer,
                        model_name=base_data.model_name,
                        operational_lifetime=base_data.lifetime,
                        rated_bounds=base_data.rated_bounds,
                        type=inverter_type,
                    )
                case unexpected_inverter_type:
                    assert_never(unexpected_inverter_type)
        case (
            ComponentCategory.POWER_TRANSFORMER | ComponentCategory.VOLTAGE_TRANSFORMER
        ):
            return VoltageTransformer(
                id=base_data.component_id,
                microgrid_id=base_data.microgrid_id,
                name=base_data.name,
                manufacturer=base_data.manufacturer,
                model_name=base_data.model_name,
                operational_lifetime=base_data.lifetime,
                rated_bounds=base_data.rated_bounds,
                primary_voltage=message.category_specific_info.power_transformer.primary,
                secondary_voltage=message.category_specific_info.power_transformer.secondary,
            )
        case unexpected_category:
            assert_never(unexpected_category)


def _trivial_category_to_class(
    category: ComponentCategory,
) -> type[
    UnspecifiedComponent
    | Chp
    | Converter
    | CryptoMiner
    | Electrolyzer
    | Hvac
    | Meter
    | Precharger
    | Relay
]:
    """Return the class corresponding to a trivial component category."""
    return {
        ComponentCategory.UNSPECIFIED: UnspecifiedComponent,
        ComponentCategory.CHP: Chp,
        ComponentCategory.CONVERTER: Converter,
        ComponentCategory.CRYPTO_MINER: CryptoMiner,
        ComponentCategory.ELECTROLYZER: Electrolyzer,
        ComponentCategory.HVAC: Hvac,
        ComponentCategory.METER: Meter,
        ComponentCategory.PRECHARGER: Precharger,
        ComponentCategory.RELAY: Relay,
    }[category]


def _metric_config_bounds_from_proto(
    message: Sequence[electrical_components_pb2.MetricConfigBounds],
    *,
    major_issues: list[str],
    minor_issues: list[str],  # pylint: disable=unused-argument
) -> dict[Metric | int, Bounds]:
    """Convert a `MetricConfigBounds` message to a dictionary of `Metric` to `Bounds`.

    Args:
        message: The `MetricConfigBounds` message.
        major_issues: A list to append major issues to.
        minor_issues: A list to append minor issues to.

    Returns:
        The resulting dictionary of `Metric` to `Bounds`.
    """
    bounds: dict[Metric | int, Bounds] = {}
    for metric_bound in message:
        metric = enum_from_proto(metric_bound.metric, Metric)
        match metric:
            case Metric.UNSPECIFIED:
                major_issues.append("metric_config_bounds has an UNSPECIFIED metric")
            case int():
                minor_issues.append(
                    f"metric_config_bounds has an unrecognized metric {metric}"
                )

        if not metric_bound.HasField("config_bounds"):
            major_issues.append(
                f"metric_config_bounds for {metric} is present but missing "
                "`config_bounds`, considering it unbounded",
            )
            continue

        try:
            bound = bounds_from_proto(metric_bound.config_bounds)
        except ValueError as exc:
            major_issues.append(
                f"metric_config_bounds for {metric} is invalid ({exc}), considering "
                "it as missing (i.e. unbouded)",
            )
            continue
        if metric in bounds:
            major_issues.append(
                f"metric_config_bounds for {metric} is duplicated in the message"
                f"using the last one ({bound})",
            )
        bounds[metric] = bound

    return bounds


def _get_operational_lifetime_from_proto(
    message: electrical_components_pb2.ElectricalComponent,
    *,
    major_issues: list[str],
    minor_issues: list[str],
) -> Lifetime:
    """Get the operational lifetime from a protobuf message."""
    if message.HasField("operational_lifetime"):
        try:
            return lifetime_from_proto(message.operational_lifetime)
        except ValueError as exc:
            major_issues.append(
                f"invalid operational lifetime ({exc}), considering it as missing "
                "(i.e. always operational)",
            )
    else:
        minor_issues.append(
            "missing operational lifetime, considering it always operational",
        )
    return Lifetime()
