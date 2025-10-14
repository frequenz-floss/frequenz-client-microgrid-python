# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Supported metrics for microgrid components."""


from frequenz.api.common.v1alpha8.metrics import metrics_pb2
from frequenz.core import enum


@enum.unique
class Metric(enum.Enum):
    """List of supported metrics.

    Note: AC energy metrics information
        - This energy metric is reported directly from the component, and not a
          result of aggregations in our systems. If a component does not have this
          metric, this field cannot be populated.

        - Components that provide energy metrics reset this metric from time to
          time. This behaviour is specific to each component model. E.g., some
          components reset it on UTC 00:00:00.

        - This energy metric does not specify the start time of the accumulation
          period,and therefore can be inconsistent.
    """

    UNSPECIFIED = metrics_pb2.METRIC_UNSPECIFIED
    """The metric is unspecified (this should not be used)."""

    DC_VOLTAGE = metrics_pb2.METRIC_DC_VOLTAGE
    """The direct current voltage."""

    DC_CURRENT = metrics_pb2.METRIC_DC_CURRENT
    """The direct current current."""

    DC_POWER = metrics_pb2.METRIC_DC_POWER
    """The direct current power."""

    AC_FREQUENCY = metrics_pb2.METRIC_AC_FREQUENCY
    """The alternating current frequency."""

    AC_VOLTAGE = metrics_pb2.METRIC_AC_VOLTAGE
    """The alternating current electric potential difference."""

    AC_VOLTAGE_PHASE_1_N = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_1_N
    """The alternating current electric potential difference between phase 1 and neutral."""

    AC_VOLTAGE_PHASE_2_N = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_2_N
    """The alternating current electric potential difference between phase 2 and neutral."""

    AC_VOLTAGE_PHASE_3_N = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_3_N
    """The alternating current electric potential difference between phase 3 and neutral."""

    AC_VOLTAGE_PHASE_1_PHASE_2 = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_1_PHASE_2
    """The alternating current electric potential difference between phase 1 and phase 2."""

    AC_VOLTAGE_PHASE_2_PHASE_3 = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_2_PHASE_3
    """The alternating current electric potential difference between phase 2 and phase 3."""

    AC_VOLTAGE_PHASE_3_PHASE_1 = metrics_pb2.METRIC_AC_VOLTAGE_PHASE_3_PHASE_1
    """The alternating current electric potential difference between phase 3 and phase 1."""

    AC_CURRENT = metrics_pb2.METRIC_AC_CURRENT
    """The alternating current current."""

    AC_CURRENT_PHASE_1 = metrics_pb2.METRIC_AC_CURRENT_PHASE_1
    """The alternating current current in phase 1."""

    AC_CURRENT_PHASE_2 = metrics_pb2.METRIC_AC_CURRENT_PHASE_2
    """The alternating current current in phase 2."""

    AC_CURRENT_PHASE_3 = metrics_pb2.METRIC_AC_CURRENT_PHASE_3
    """The alternating current current in phase 3."""

    AC_POWER_APPARENT = metrics_pb2.METRIC_AC_POWER_APPARENT
    """The alternating current apparent power."""

    AC_APPARENT_POWER = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_APPARENT,
        "AC_APPARENT_POWER is deprecated, use AC_POWER_APPARENT instead",
    )
    """The alternating current apparent power (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_APPARENT`][frequenz.client.microgrid.metrics.Metric.AC_POWER_APPARENT]
        instead.
    """

    AC_POWER_APPARENT_PHASE_1 = metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_1
    """The alternating current apparent power in phase 1."""

    AC_APPARENT_POWER_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_1,
        "AC_APPARENT_POWER_PHASE_1 is deprecated, use AC_POWER_APPARENT_PHASE_1 instead",
    )
    """The alternating current apparent power in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_APPARENT_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_POWER_APPARENT_PHASE_1]
        instead.
    """

    AC_POWER_APPARENT_PHASE_2 = metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_2
    """The alternating current apparent power in phase 2."""

    AC_APPARENT_POWER_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_2,
        "AC_APPARENT_POWER_PHASE_2 is deprecated, use AC_POWER_APPARENT_PHASE_2 instead",
    )
    """The alternating current apparent power in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_APPARENT_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_POWER_APPARENT_PHASE_2]
        instead.
    """

    AC_POWER_APPARENT_PHASE_3 = metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_3
    """The alternating current apparent power in phase 3."""

    AC_APPARENT_POWER_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_APPARENT_PHASE_3,
        "AC_APPARENT_POWER_PHASE_3 is deprecated, use AC_POWER_APPARENT_PHASE_3 instead",
    )
    """The alternating current apparent power in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_APPARENT_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_POWER_APPARENT_PHASE_3]
        instead.
    """

    AC_POWER_ACTIVE = metrics_pb2.METRIC_AC_POWER_ACTIVE
    """The alternating current active power."""

    AC_ACTIVE_POWER = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_ACTIVE,
        "AC_ACTIVE_POWER is deprecated, use AC_POWER_ACTIVE instead",
    )
    """The alternating current active power (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_ACTIVE`][frequenz.client.microgrid.metrics.Metric.AC_POWER_ACTIVE]
        instead.
    """

    AC_POWER_ACTIVE_PHASE_1 = metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_1
    """The alternating current active power in phase 1."""

    AC_ACTIVE_POWER_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_1,
        "AC_ACTIVE_POWER_PHASE_1 is deprecated, use AC_POWER_ACTIVE_PHASE_1 instead",
    )
    """The alternating current active power in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_ACTIVE_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_POWER_ACTIVE_PHASE_1]
        instead.
    """

    AC_POWER_ACTIVE_PHASE_2 = metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_2
    """The alternating current active power in phase 2."""

    AC_ACTIVE_POWER_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_2,
        "AC_ACTIVE_POWER_PHASE_2 is deprecated, use AC_POWER_ACTIVE_PHASE_2 instead",
    )
    """The alternating current active power in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_ACTIVE_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_POWER_ACTIVE_PHASE_2]
        instead.
    """

    AC_POWER_ACTIVE_PHASE_3 = metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_3
    """The alternating current active power in phase 3."""

    AC_ACTIVE_POWER_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_ACTIVE_PHASE_3,
        "AC_ACTIVE_POWER_PHASE_3 is deprecated, use AC_POWER_ACTIVE_PHASE_3 instead",
    )
    """The alternating current active power in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_ACTIVE_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_POWER_ACTIVE_PHASE_3]
        instead.
    """

    AC_POWER_REACTIVE = metrics_pb2.METRIC_AC_POWER_REACTIVE
    """The alternating current reactive power."""

    AC_REACTIVE_POWER = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_REACTIVE,
        "AC_REACTIVE_POWER is deprecated, use AC_POWER_REACTIVE instead",
    )
    """The alternating current reactive power (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_REACTIVE`][frequenz.client.microgrid.metrics.Metric.AC_POWER_REACTIVE]
        instead.
    """

    AC_POWER_REACTIVE_PHASE_1 = metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_1
    """The alternating current reactive power in phase 1."""

    AC_REACTIVE_POWER_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_1,
        "AC_REACTIVE_POWER_PHASE_1 is deprecated, use AC_POWER_REACTIVE_PHASE_1 instead",
    )
    """The alternating current reactive power in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_REACTIVE_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_POWER_REACTIVE_PHASE_1]
        instead.
    """

    AC_POWER_REACTIVE_PHASE_2 = metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_2
    """The alternating current reactive power in phase 2."""

    AC_REACTIVE_POWER_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_2,
        "AC_REACTIVE_POWER_PHASE_2 is deprecated, use AC_POWER_REACTIVE_PHASE_2 instead",
    )
    """The alternating current reactive power in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_REACTIVE_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_POWER_REACTIVE_PHASE_2]
        instead.
    """

    AC_POWER_REACTIVE_PHASE_3 = metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_3
    """The alternating current reactive power in phase 3."""

    AC_REACTIVE_POWER_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_POWER_REACTIVE_PHASE_3,
        "AC_REACTIVE_POWER_PHASE_3 is deprecated, use AC_POWER_REACTIVE_PHASE_3 instead",
    )
    """The alternating current reactive power in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_POWER_REACTIVE_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_POWER_REACTIVE_PHASE_3]
        instead.
    """

    AC_POWER_FACTOR = metrics_pb2.METRIC_AC_POWER_FACTOR
    """The alternating current power factor."""

    AC_POWER_FACTOR_PHASE_1 = metrics_pb2.METRIC_AC_POWER_FACTOR_PHASE_1
    """The alternating current power factor in phase 1."""

    AC_POWER_FACTOR_PHASE_2 = metrics_pb2.METRIC_AC_POWER_FACTOR_PHASE_2
    """The alternating current power factor in phase 2."""

    AC_POWER_FACTOR_PHASE_3 = metrics_pb2.METRIC_AC_POWER_FACTOR_PHASE_3
    """The alternating current power factor in phase 3."""

    AC_ENERGY_APPARENT = metrics_pb2.METRIC_AC_ENERGY_APPARENT
    """The alternating current apparent energy."""

    AC_APPARENT_ENERGY = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_APPARENT,
        "AC_APPARENT_ENERGY is deprecated, use AC_ENERGY_APPARENT instead",
    )
    """The alternating current apparent energy (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_APPARENT`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_APPARENT]
        instead.
    """

    AC_ENERGY_APPARENT_PHASE_1 = metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_1
    """The alternating current apparent energy in phase 1."""

    AC_APPARENT_ENERGY_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_1,
        "AC_APPARENT_ENERGY_PHASE_1 is deprecated, use AC_ENERGY_APPARENT_PHASE_1 instead",
    )
    """The alternating current apparent energy in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_APPARENT_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_APPARENT_PHASE_1]
        instead.
    """

    AC_ENERGY_APPARENT_PHASE_2 = metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_2
    """The alternating current apparent energy in phase 2."""

    AC_APPARENT_ENERGY_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_2,
        "AC_APPARENT_ENERGY_PHASE_2 is deprecated, use AC_ENERGY_APPARENT_PHASE_2 instead",
    )
    """The alternating current apparent energy in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_APPARENT_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_APPARENT_PHASE_2]
        instead.
    """

    AC_ENERGY_APPARENT_PHASE_3 = metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_3
    """The alternating current apparent energy in phase 3."""

    AC_APPARENT_ENERGY_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_APPARENT_PHASE_3,
        "AC_APPARENT_ENERGY_PHASE_3 is deprecated, use AC_ENERGY_APPARENT_PHASE_3 instead",
    )
    """The alternating current apparent energy in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_APPARENT_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_APPARENT_PHASE_3]
        instead.
    """

    AC_ENERGY_ACTIVE = metrics_pb2.METRIC_AC_ENERGY_ACTIVE
    """The alternating current active energy."""

    AC_ACTIVE_ENERGY = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE,
        "AC_ACTIVE_ENERGY is deprecated, use AC_ENERGY_ACTIVE instead",
    )
    """The alternating current active energy (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE]
        instead.
    """

    AC_ENERGY_ACTIVE_PHASE_1 = metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_1
    """The alternating current active energy in phase 1."""

    AC_ACTIVE_ENERGY_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_1,
        "AC_ACTIVE_ENERGY_PHASE_1 is deprecated, use AC_ENERGY_ACTIVE_PHASE_1 instead",
    )
    """The alternating current active energy in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_PHASE_1]
        instead.
    """

    AC_ENERGY_ACTIVE_PHASE_2 = metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_2
    """The alternating current active energy in phase 2."""

    AC_ACTIVE_ENERGY_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_2,
        "AC_ACTIVE_ENERGY_PHASE_2 is deprecated, use AC_ENERGY_ACTIVE_PHASE_2 instead",
    )
    """The alternating current active energy in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_PHASE_2]
        instead.
    """

    AC_ENERGY_ACTIVE_PHASE_3 = metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_3
    """The alternating current active energy in phase 3."""

    AC_ACTIVE_ENERGY_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_PHASE_3,
        "AC_ACTIVE_ENERGY_PHASE_3 is deprecated, use AC_ENERGY_ACTIVE_PHASE_3 instead",
    )
    """The alternating current active energy in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_PHASE_3]
        instead.
    """

    AC_ENERGY_ACTIVE_CONSUMED = metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED
    """The alternating current active energy consumed."""

    AC_ACTIVE_ENERGY_CONSUMED = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED,
        "AC_ACTIVE_ENERGY_CONSUMED is deprecated, use AC_ENERGY_ACTIVE_CONSUMED instead",
    )
    """The alternating current active energy consumed (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_CONSUMED`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_CONSUMED]
        instead.
    """

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_1 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_1
    )
    """The alternating current active energy consumed in phase 1."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_1,
        "AC_ACTIVE_ENERGY_CONSUMED_PHASE_1 is deprecated, use AC_ENERGY_ACTIVE_CONSUMED_PHASE_1 instead",
    )
    """The alternating current active energy consumed in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_CONSUMED_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_CONSUMED_PHASE_1]
        instead.
    """

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_2 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_2
    )
    """The alternating current active energy consumed in phase 2."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_2,
        "AC_ACTIVE_ENERGY_CONSUMED_PHASE_2 is deprecated, use AC_ENERGY_ACTIVE_CONSUMED_PHASE_2 instead",
    )
    """The alternating current active energy consumed in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_CONSUMED_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_CONSUMED_PHASE_2]
        instead.
    """

    AC_ENERGY_ACTIVE_CONSUMED_PHASE_3 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_3
    )
    """The alternating current active energy consumed in phase 3."""

    AC_ACTIVE_ENERGY_CONSUMED_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_CONSUMED_PHASE_3,
        "AC_ACTIVE_ENERGY_CONSUMED_PHASE_3 is deprecated, use AC_ENERGY_ACTIVE_CONSUMED_PHASE_3 instead",
    )
    """The alternating current active energy consumed in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_CONSUMED_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_CONSUMED_PHASE_3]
        instead.
    """

    AC_ENERGY_ACTIVE_DELIVERED = metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED
    """The alternating current active energy delivered."""

    AC_ACTIVE_ENERGY_DELIVERED = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED,
        "AC_ACTIVE_ENERGY_DELIVERED is deprecated, use AC_ENERGY_ACTIVE_DELIVERED instead",
    )
    """The alternating current active energy delivered (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_DELIVERED`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_DELIVERED]
        instead.
    """

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_1 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_1
    )
    """The alternating current active energy delivered in phase 1."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_1,
        "AC_ACTIVE_ENERGY_DELIVERED_PHASE_1 is deprecated, use AC_ENERGY_ACTIVE_DELIVERED_PHASE_1 instead",
    )
    """The alternating current active energy delivered in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_DELIVERED_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_DELIVERED_PHASE_1]
        instead.
    """

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_2 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_2
    )
    """The alternating current active energy delivered in phase 2."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_2,
        "AC_ACTIVE_ENERGY_DELIVERED_PHASE_2 is deprecated, use AC_ENERGY_ACTIVE_DELIVERED_PHASE_2 instead",
    )
    """The alternating current active energy delivered in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_DELIVERED_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_DELIVERED_PHASE_2]
        instead.
    """

    AC_ENERGY_ACTIVE_DELIVERED_PHASE_3 = (
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_3
    )
    """The alternating current active energy delivered in phase 3."""

    AC_ACTIVE_ENERGY_DELIVERED_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_ACTIVE_DELIVERED_PHASE_3,
        "AC_ACTIVE_ENERGY_DELIVERED_PHASE_3 is deprecated, use AC_ENERGY_ACTIVE_DELIVERED_PHASE_3 instead",
    )
    """The alternating current active energy delivered in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_ACTIVE_DELIVERED_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_ACTIVE_DELIVERED_PHASE_3]
        instead.
    """

    AC_ENERGY_REACTIVE = metrics_pb2.METRIC_AC_ENERGY_REACTIVE
    """The alternating current reactive energy."""

    AC_REACTIVE_ENERGY = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_REACTIVE,
        "AC_REACTIVE_ENERGY is deprecated, use AC_ENERGY_REACTIVE instead",
    )
    """The alternating current reactive energy (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_REACTIVE`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_REACTIVE]
        instead.
    """

    AC_ENERGY_REACTIVE_PHASE_1 = metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_1
    """The alternating current reactive energy in phase 1."""

    AC_REACTIVE_ENERGY_PHASE_1 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_1,
        "AC_REACTIVE_ENERGY_PHASE_1 is deprecated, use AC_ENERGY_REACTIVE_PHASE_1 instead",
    )
    """The alternating current reactive energy in phase 1 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_REACTIVE_PHASE_1`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_REACTIVE_PHASE_1]
        instead.
    """

    AC_ENERGY_REACTIVE_PHASE_2 = metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_2
    """The alternating current reactive energy in phase 2."""

    AC_REACTIVE_ENERGY_PHASE_2 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_2,
        "AC_REACTIVE_ENERGY_PHASE_2 is deprecated, use AC_ENERGY_REACTIVE_PHASE_2 instead",
    )
    """The alternating current reactive energy in phase 2 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_REACTIVE_PHASE_2`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_REACTIVE_PHASE_2]
        instead.
    """

    AC_ENERGY_REACTIVE_PHASE_3 = metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_3
    """The alternating current reactive energy in phase 3."""

    AC_REACTIVE_ENERGY_PHASE_3 = enum.deprecated_member(
        metrics_pb2.METRIC_AC_ENERGY_REACTIVE_PHASE_3,
        "AC_REACTIVE_ENERGY_PHASE_3 is deprecated, use AC_ENERGY_REACTIVE_PHASE_3 instead",
    )
    """The alternating current reactive energy in phase 3 (deprecated).

    Deprecated: Deprecated in v0.18.0
        Use [`AC_ENERGY_REACTIVE_PHASE_3`][frequenz.client.microgrid.metrics.Metric.AC_ENERGY_REACTIVE_PHASE_3]
        instead.
    """

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT = (
        metrics_pb2.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT
    )
    """The alternating current total harmonic distortion current."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1 = (
        metrics_pb2.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1
    )
    """The alternating current total harmonic distortion current in phase 1."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2 = (
        metrics_pb2.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2
    )
    """The alternating current total harmonic distortion current in phase 2."""

    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3 = (
        metrics_pb2.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3
    )
    """The alternating current total harmonic distortion current in phase 3."""

    BATTERY_CAPACITY = metrics_pb2.METRIC_BATTERY_CAPACITY
    """The capacity of the battery."""

    BATTERY_SOC_PCT = metrics_pb2.METRIC_BATTERY_SOC_PCT
    """The state of charge of the battery as a percentage."""

    BATTERY_TEMPERATURE = metrics_pb2.METRIC_BATTERY_TEMPERATURE
    """The temperature of the battery."""

    INVERTER_TEMPERATURE = metrics_pb2.METRIC_INVERTER_TEMPERATURE
    """The temperature of the inverter."""

    INVERTER_TEMPERATURE_CABINET = metrics_pb2.METRIC_INVERTER_TEMPERATURE_CABINET
    """The temperature of the inverter cabinet."""

    INVERTER_TEMPERATURE_HEATSINK = metrics_pb2.METRIC_INVERTER_TEMPERATURE_HEATSINK
    """The temperature of the inverter heatsink."""

    INVERTER_TEMPERATURE_TRANSFORMER = (
        metrics_pb2.METRIC_INVERTER_TEMPERATURE_TRANSFORMER
    )
    """The temperature of the inverter transformer."""

    EV_CHARGER_TEMPERATURE = metrics_pb2.METRIC_EV_CHARGER_TEMPERATURE
    """The temperature of the EV charger."""

    SENSOR_WIND_SPEED = metrics_pb2.METRIC_SENSOR_WIND_SPEED
    """The speed of the wind measured."""

    SENSOR_WIND_DIRECTION = metrics_pb2.METRIC_SENSOR_WIND_DIRECTION
    """The direction of the wind measured."""

    SENSOR_TEMPERATURE = metrics_pb2.METRIC_SENSOR_TEMPERATURE
    """The temperature measured."""

    SENSOR_RELATIVE_HUMIDITY = metrics_pb2.METRIC_SENSOR_RELATIVE_HUMIDITY
    """The relative humidity measured."""

    SENSOR_DEW_POINT = metrics_pb2.METRIC_SENSOR_DEW_POINT
    """The dew point measured."""

    SENSOR_AIR_PRESSURE = metrics_pb2.METRIC_SENSOR_AIR_PRESSURE
    """The air pressure measured."""

    SENSOR_IRRADIANCE = metrics_pb2.METRIC_SENSOR_IRRADIANCE
    """The irradiance measured."""
