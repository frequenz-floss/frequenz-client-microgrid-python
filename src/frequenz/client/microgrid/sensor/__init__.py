# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Microgrid sensors.

This package provides classes and utilities for working with different types of
sensors in a microgrid environment. Sensors measure various physical metrics in
the surrounding environment, such as temperature, humidity, and solar
irradiance.

# Sensor Class Hierarchy

All sensors in this package inherit from the base
[`Sensor`][frequenz.client.microgrid.sensor.Sensor] class, which provides common
attributes and functionality.

The sensors are divided into two main categories:

## Well-known Sensors

These are well-defined sensor types that directly inherit from `Sensor`:

* [`Accelerometer`][frequenz.client.microgrid.sensor.Accelerometer]: Measures
    acceleration.
* [`Anemometer`][frequenz.client.microgrid.sensor.Anemometer]: Measures wind
    velocity and direction.
* [`Barometer`][frequenz.client.microgrid.sensor.Barometer]: Measures
    atmospheric pressure.
* [`GeneralSensor`][frequenz.client.microgrid.sensor.GeneralSensor]: A sensor
    type that doesn't fit into other categories.
* [`Hygrometer`][frequenz.client.microgrid.sensor.Hygrometer]: Measures
    humidity.
* [`Pyranometer`][frequenz.client.microgrid.sensor.Pyranometer]: Measures solar
    irradiance.
* [`Thermometer`][frequenz.client.microgrid.sensor.Thermometer]: Measures
    temperature.

## Problematic Sensors

These special types handle cases where sensor data from the API cannot be
cleanly mapped to a well-known sensor type. They inherit from
[`ProblematicSensor`][frequenz.client.microgrid.sensor.ProblematicSensor],
(which itself inherits from `Sensor`):

* [`UnspecifiedSensor`][frequenz.client.microgrid.sensor.UnspecifiedSensor]:
    Used when the sensor's type is not specified in the API data.
* [`UnrecognizedSensor`][frequenz.client.microgrid.sensor.UnrecognizedSensor]:
    Used when the sensor type specified in the API is unknown to this client
    version (e.g., a new sensor type was added after this client was released).
* [`MismatchedCategorySensor`][frequenz.client.microgrid.sensor.MismatchedCategorySensor]:
    Used when a sensor has the wrong `COMPONENT_CATEGORY_SENSOR` category in the
    API and there is also no sensor metadata to determine the correct sensor
    type.

# Working with Sensors

The [`SensorTypes`][frequenz.client.microgrid.sensor.SensorTypes] type alias
represents a union of all possible sensor types. You can use Python's type
checking features to work with different sensor types.

A [`ProblematicSensorTypes`][frequenz.client.microgrid.sensor.ProblematicSensorTypes]
type alias is also provided, which includes all problematic sensor types.

This allows you to handle sensors that may not fit into the well-known sensor
types as a group.

Example: Using match statements to process sensors
    The match statement can be used to handle different sensor types in a clean and
    efficient way. The type-checker can then do [exhaustiveness
    checking](https://mypy.readthedocs.io/en/stable/literal_types.html#id3) to
    ensure that all possible sensor types are handled.

    ```python
    from typing import assert_never

    def process_sensor(sensor: SensorTypes) -> None:
        match sensor:
            case Accelerometer():
                print("Processing acceleration sensor")
            case Anemometer():
                print("Processing wind sensor")
            case Barometer():
                print("Processing pressure sensor")
            case GeneralSensor():
                print("Processing general sensor")
            case Hygrometer():
                print("Processing humidity sensor")
            case Pyranometer():
                print("Processing solar irradiance sensor")
            case Thermometer():
                print("Processing temperature sensor")
            case UnspecifiedSensor():
                print("Processing unknown sensor")
            case UnrecognizedSensor():
                print("Processing unrecognized sensor")
            case MismatchedCategorySensor():
                print("Processing misconfigured sensor")
            case unexpected:
                assert_never(unexpected)
    ```

Example: Processing problematic sensors as a group
    ```python
    from typing import assert_never

    def process_sensor(sensor: SensorTypes) -> None:
        match sensor:
            case Accelerometer():
                print("Processing acceleration sensor")
            case Anemometer():
                print("Processing wind sensor")
            case Barometer():
                print("Processing pressure sensor")
            case GeneralSensor():
                print("Processing general sensor")
            case Hygrometer():
                print("Processing humidity sensor")
            case Pyranometer():
                print("Processing solar irradiance sensor")
            case Thermometer():
                print("Processing temperature sensor")
            case ProblematicSensor():
                print("Processing unknown sensor")
            case unexpected:
                assert_never(unexpected)
    ```
"""

from ._accelerometer import Accelerometer
from ._anemometer import Anemometer
from ._barometer import Barometer
from ._base import Sensor
from ._category import SensorCategory
from ._general_sensor import GeneralSensor
from ._hygrometer import Hygrometer
from ._problematic import (
    MismatchedCategorySensor,
    ProblematicSensor,
    UnrecognizedSensor,
    UnspecifiedSensor,
)
from ._pyranometer import Pyranometer
from ._thermometer import Thermometer
from ._types import ProblematicSensorTypes, SensorTypes

__all__ = [
    "Accelerometer",
    "Anemometer",
    "Barometer",
    "GeneralSensor",
    "Hygrometer",
    "MismatchedCategorySensor",
    "ProblematicSensor",
    "ProblematicSensorTypes",
    "Pyranometer",
    "Sensor",
    "SensorCategory",
    "SensorTypes",
    "Thermometer",
    "UnrecognizedSensor",
    "UnspecifiedSensor",
]
