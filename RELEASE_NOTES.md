# Frequenz Microgrid API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- `ComponentCategory` is now being imported from `frequenz-client-common` v0.3.3. This means:

    * You need to add/update the minimum dependency to `frequenz-client-common`
    * `ComponentCategory.NONE` is not named `ComponentCategory.UNSPECIFIED`
    * `Component.category` has now the type `ComponentCategory | int`.
    * Before if a category that had no corresponding value in `ComponentCategory` was received (the server is probably using a newer version with a new category), `ComponentCategory.NONE` was used. Now we keep the original `int` received from protobuf. This allows to use an old client version with a new server, as long as the user knows how to interpret the `int` value, so it provided more flexibility.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
