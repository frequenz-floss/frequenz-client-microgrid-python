# Frequenz Microgrid API Client Release Notes

## Summary

This release removes the `timezonefinder` dependency to significantly reduce package size by 66M+ and enable ARM platform support.

> [!WARNING]
>  This is a **breaking change** shipped in a patch release because this feature has no known users.

## Upgrading

The `Location.timezone` field no longer performs automatic timezone lookup from latitude/longitude coordinates.

```python
# Automatic timezone lookup (no longer works)
location = Location(latitude=52.52, longitude=13.405)
print(location.timezone)  # Previously: ZoneInfo('Europe/Berlin'), now None
```

If you need timezone lookup from coordinates, install [`timezonefinder`](https://pypi.org/project/timezonefinder/) separately and implement manual lookup:

```python
# Install: pip install timezonefinder
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from frequenz.client.microgrid import Location

tf = TimezoneFinder()
tz_name = tf.timezone_at(lat=52.52, lng=13.405)
timezone = ZoneInfo(tz_name) if tz_name else None
location = Location(latitude=52.52, longitude=13.405, timezone=timezone)
```
