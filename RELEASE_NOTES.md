# Frequenz Microgrid API Client Release Notes

## Summary

This release adds a new `WindTurbine` component type.

## Upgrading

- If you are using `match` and doing exhaustive matching on the `Component` types, you will get `mypy` errors and will need to handle the new `WindTurbine` type.

## New Features

- Add `WindTurbine` component type.
