# Strawberry Chat - v1.13.1 Stable
Hello!! After a long time, I felt compelled to release a new version of Strawberry Chat. 
Due to school stress (and other stress), I unfortunately didn't have time for it. But today there's a new release.

This release is relatively small, as it only contains minor fixes. The “biggest” change is probably the change of the Rust edition from 2021 to 2024 and the API migration from stblib to libstrawberry.

# Changelog

- ![](https://img.shields.io/badge/-Deps-blue) Updated edition to 2024 and dependencies to latest versions
- ![](https://img.shields.io/badge/-Deps-blue) Updated dependencies (stblib, async-trait, etc.) to latest versions
- ![](https://img.shields.io/badge/-Deps-blue) Removed owocolors
- ![](https://img.shields.io/badge/-Fix-red) Migrated from stblib to libstrawberry
- ![](https://img.shields.io/badge/-Fix-red) Fixed Strawberry API version and URLs
- ![](https://img.shields.io/badge/-Fix-red) Improved warning log messages and format for Strawberry API connection issues
- ![](https://img.shields.io/badge/-Fix-red) Removed unnecessary PartialEq and Eq derives from Command struct
- ![](https://img.shields.io/badge/-Fix-red) Replaced lazy_static with LazyLock in global, db, and server_core modules
- ![](https://img.shields.io/badge/-Fix-red) Corrected loop termination syntax and replaced continue with no-op in client_login function
- ![](https://img.shields.io/badge/-Fix-red) Addressed cargo clippy warnings
- ![](https://img.shields.io/badge/-Refactor-purple) Simplified badge list creation in create_badge_list function
- ![](https://img.shields.io/badge/-Refactor-purple) Updated parse_user_status to return both symbol and text representation
- ![](https://img.shields.io/badge/-Refactor-purple) Streamlined message handling logic
- ![](https://img.shields.io/badge/-Refactor-purple) Replaced panic_crash with panic in database and config modules
- ![](https://img.shields.io/badge/-Feat-success) Added online mode display to feature output

## Pull requests
*There are no pull requests*

## Issues / Milestone
*There are no issues*

# TL;DR
This version updates Strawberry Chat to Rust Edition 2024 and brings all dependencies up to date. The API was migrated from stblib to libstrawberry, including improvements to versioning, URLs, and log messages. The code was refactored in several areas for better readability and efficiency, such as badge list creation, user status output, and message handling. Unused dependencies and derives were removed, clippy warnings addressed, and lazy_static replaced with LazyLock. Additionally, the feature output now displays online mode.

## Next release?
See https://github.com/Strawberry-Foundations/strawberry-chat#release-cycle

**Full Changelog**: https://github.com/Strawberry-Foundations/strawberry-chat/compare/v1.13.0...v1.13.1