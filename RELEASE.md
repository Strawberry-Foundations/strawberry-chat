# Strawberry Chat - v1.13.0 Stable
Hey everyone. Tonight (at least in Europe) I am releasing v1.13.0 of Strawberry Chat.
This release includes some important bug fixes and quality of life improvements.

# Changelog
- ![](https://img.shields.io/badge/-New-success) Added list-badges subcommand for /admin-settings
- ![](https://img.shields.io/badge/-New-success) Added automatic addition of the Strawberry badge when the user connects to the Strawberry ID
- ![](https://img.shields.io/badge/-New-success) Remove unused config flags
- ![](https://img.shields.io/badge/-New-success) Updated logging
- ![](https://img.shields.io/badge/-New-success) Add `max_message_length` for Rust-rewrite
- ![](https://img.shields.io/badge/-New-success) Revamped database system (Support for MySQL, SQLite & PostgreSQL - more coming soon!)
- ![](https://img.shields.io/badge/-New-success) Lots of optimization for the database system
- ![](https://img.shields.io/badge/-New-success) Use the configuration `database_table` to use the correct table (#147)
- ![](https://img.shields.io/badge/-New-success) Check if the given table in the configuration exists - If not create one
- ![](https://img.shields.io/badge/-New-success) Update core to v1.04
- ![](https://img.shields.io/badge/-Fix-red) Fixed a panic occurred by /admin-settings
- ![](https://img.shields.io/badge/-Fix-red) Fixed a panic occurred by /kick
- ![](https://img.shields.io/badge/-Fix-red) Fixed use of deprecated type alias std::panic::PanicInfo
- ![](https://img.shields.io/badge/-Fix-red) Code optimizations
- ![](https://img.shields.io/badge/-Fix-red) Fixed custom database port not working (#150)
- ![](https://img.shields.io/badge/-Optimization-9cf) General code optimizations
- ![](https://img.shields.io/badge/-Optimization-9cf) Improved logging
- ![](https://img.shields.io/badge/-Optimization-9cf) Internal database optimizations
- ![](https://img.shields.io/badge/-Chore-yellow) Several dependency updates
- ![](https://img.shields.io/badge/-Chore-yellow) Moved cryptographic functions to separate module

## Pull requests
* ENHANCEMENT: Database System Revamp (Milestone) by @Juliandev02 in https://github.com/Strawberry-Foundations/strawberry-chat/pull/152

## Issues / Milestone
- #147
- #148
- #149
- #150
- #151
- #152

# TL;DR
With v1.13 we have implemented a new multifunctional database system which will support MySQL, SQLite and in future also PostgreSQL.
The new system simplifies the implementation of new or other database systems.
There are some bug fixes regarding commands, a few functions from the legacy Python version have been taken over and some things have been optimized.

## Next release?
See https://github.com/Strawberry-Foundations/strawberry-chat#release-cycle

**Full Changelog**: https://github.com/Strawberry-Foundations/strawberry-chat/compare/v1.12.0...v1.13.0