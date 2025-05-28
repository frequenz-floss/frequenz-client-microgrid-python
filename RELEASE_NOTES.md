# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

* When receiving streaming data for components, you now need to handle the receiving of the types `StreamStarted`, `StreamRetrying`, `StreamFatalError`. If you don't care about the new events and just want the old behavior your can always use `filter_stream_events` to ignore them, for example:

    ```python
    from frequenz.client.base.streaming import filter_stream_events

    meter_rx = filter_stream_events(await client.meter_data())
    ```

## New Features

* Using the latest streaming client, when using `stream_sensor_data()` you will now get stream notification events, such as `StreamStarted`, `StreamRetrying` and `StreamFatalError`, which can be used to monitor the state of the stream.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
