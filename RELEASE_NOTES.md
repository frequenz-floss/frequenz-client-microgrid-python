# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Now component and microgrid IDs are wrapped in new classes: `ComponentId` and `MicrogridId` respectively.

   These classes provide type safety and prevent accidental errors by:

   - Making it impossible to mix up microgrid and component IDs (equality comparisons between different ID types always return false).
   - Preventing accidental math operations on IDs.
   - Providing clear string representations for debugging (MID42, CID42).
   - Ensuring proper hash behavior in collections.

   To migrate you just need to wrap your `int` IDs with the appropriate class: `0` -> `ComponentId(0)` / `MicrogridId(0)`.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
