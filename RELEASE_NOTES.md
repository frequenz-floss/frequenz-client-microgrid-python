# Frequenz Microgrid API Client Release Notes

## Summary

This release introduces sensors support and adds official support for Python 3.12. It also includes some bug fixes.

## Upgrading

- Some minimum versions of dependencies have been bumped to support Python 3.12. You might also need to bump these dependencies in your project.

## New Features

- The `MicrogridApiClient` can now list sensor retrieving their metadata (`list_sensors()`) and can stream sensor data (`stream_sensor_data()`).

## Bug Fixes

- When retrieving the microgrid metadata using `metadata()`, if the location was empty in the protobuf message, a wrong location with long=0, lat=0 was used. Now the location will be properly set to `None` in that case.
- The client now does some missing cleanup (stopping background tasks) when disconnecting (and when used as a context manager).
