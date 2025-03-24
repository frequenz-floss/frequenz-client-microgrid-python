# Frequenz Microgrid API Client Release Notes

## Upgrading

- Now component and microgrid IDs are wrapped in new classes: `ComponentId` and `MicrogridId` respectively.

   These classes provide type safety and prevent accidental errors by:

   - Making it impossible to mix up microgrid and component IDs (equality comparisons between different ID types always return false).
   - Preventing accidental math operations on IDs.
   - Providing clear string representations for debugging (MID42, CID42).
   - Ensuring proper hash behavior in collections.

   To migrate you just need to wrap your `int` IDs with the appropriate class: `0` -> `ComponentId(0)` / `MicrogridId(0)`.
