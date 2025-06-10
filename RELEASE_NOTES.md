# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Some minimum dependency versions are bumped, so you might need to update your dependencies as well.
- The IDs (`MicrogridId`, `ComponentId`, `SensorId`) are now imported from `frequenz-client-common`. Please add it to your dependencies if you haven't already, then you can replace your imports:

    * `from frequenz.client.microgrid import MicrogridId` -> `from frequenz.client.common.microgrid import MicrogridId`
    * `from frequenz.client.microgrid import ComponentId` -> `from frequenz.client.common.microgrid.components import ComponentId`
    * `from frequenz.client.microgrid import SensorId` -> `from frequenz.client.common.microgrid.sensors import SensorId`

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
