# Strawberry Chat - v1.11.0 Stable
Hey! Today we are releasing v1.11.0 of Strawberry Chat, which is the result of 5 months of development.

Version 1.11.0 brings many changes - including a completely new codebase written in Rust, and much more.

We have also published version 3 of our Communication Standard.
Now server and client communicate bidirectionally with JSON data.

Due to a spontaneous decision at the end of December 2023, we had to stop the development of v1.10 early,
as we had already started with this version. We were therefore unable to make a Rust release from this version,
as we had started writing v1.10 in Python. So don't be surprised if there is no 'official' v1.10 but this changelog still
contains changes from v1.10.

# Changelog - v1.10

- ![](https://img.shields.io/badge/-New-success) Added config file error when using an outdated config file (#106)
- ![](https://img.shields.io/badge/-New-success) Added IP-Banning (#111)
- ![](https://img.shields.io/badge/-New-success) Added Windows/Mac/Linux System Notification when getting pinged (configurable) (#114)
- ![](https://img.shields.io/badge/-New-success) Added error handling if address is already in use
- ![](https://img.shields.io/badge/-New-success) Added system notification when receiving a dm (#116)
- ![](https://img.shields.io/badge/-New-success) Added specific restrictions for username (only lowercase, a - z, 0 - 9, dots, underscore) (#122)
- ![](https://img.shields.io/badge/-New-success) Added username length checking
- ![](https://img.shields.io/badge/-New-success) Added max_username_length & max_password_length config + moved some values to config yml
- ![](https://img.shields.io/badge/-New-success) Added rate limiting (#129)
- ![](https://img.shields.io/badge/-New-success) Added configuration for ratelimit (Enabling or disabling ratelimit + ratelimit timeout)


# Changelog - v1.11 (Rusty)
- ![](https://img.shields.io/badge/-Important-important) Changed code base language to Rust (see #135)
- ![](https://img.shields.io/badge/-Important-important) Complete new code structure (core-based structure)
- ![](https://img.shields.io/badge/-Important-important) We changed our Communication Standard to v3 ([German documentation for v3](https://developers.strawberryfoundations.xyz/german/json-communication/introduction#versionen-des-strawberry-communication-standards))


- ![](https://img.shields.io/badge/-New-success) MySQL Database as main database (#99)
- ![](https://img.shields.io/badge/-New-success) New rust-based clients for rust-based Strawberry Chat (CLI and TUI)
- ![](https://img.shields.io/badge/-New-success) Added improved Automod (Security)
- ![](https://img.shields.io/badge/-New-success) Added login verification (check if you're really logged in) (Security)
- ![](https://img.shields.io/badge/-New-success) Added improved message verification (Security)
- ![](https://img.shields.io/badge/-New-success) Added Watchdog (Security)
- ![](https://img.shields.io/badge/-New-success) Added automatic config creation (if no config exists)
- ![](https://img.shields.io/badge/-New-success) Added msgpack as a compression method
- ![](https://img.shields.io/badge/-New-success) Added small but fine cli "windows"
- ![](https://img.shields.io/badge/-New-success) Added new logging system (stblib)
- ![](https://img.shields.io/badge/-New-success) Custom Strawberry Chat rust library for accessing Strawberry Chat's packets
- ![](https://img.shields.io/badge/-New-success) Removed server settings (security risk)
- ![](https://img.shields.io/badge/-New-success) Removed admin user settings (security risk)


- ![](https://img.shields.io/badge/-Fix-informational) Sometimes you cannot write after mentioning a user (#125) (fixed by Rust-rewrite)
- ![](https://img.shields.io/badge/-Fix-informational) Fixed add automatic command for invalid session removal (#130) (fixed by Rust-rewrite)


- ![](https://img.shields.io/badge/-Optimization-9cf) Memory safety!
- ![](https://img.shields.io/badge/-Optimization-9cf) Improve performance by not accessing the database every time when writing something (instead use caching) (#98) (fixed by Rust-rewrite)
- ![](https://img.shields.io/badge/-Optimization-9cf) Improved error handling


- ![](https://img.shields.io/badge/-SCAPI-yellow) Scapi API Wrapper for scs.v3 (Python)


- ![](https://img.shields.io/badge/-API-cyan) Added Rust API for scs.v3
- ![](https://img.shields.io/badge/-API-cyan) Added Python API for scs.v3
- ![](https://img.shields.io/badge/-API-cyan) Added Java API for scs.v3


# Pull requests
* [Snyk] Security upgrade werkzeug from 2.2.3 to 2.3.8 by @Paddyk45 in https://github.com/Strawberry-Foundations/strawberry-chat/pull/104
* Strawberry Chat: Rust Rewrite by @Juliandev02 in https://github.com/Strawberry-Foundations/strawberry-chat/pull/136
* small event hooking system by @Paddyk45 in https://github.com/Strawberry-Foundations/strawberry-chat/pull/141

# TL;DR
- Rewrite in the Rust programming language
- New communication standard (v3), now the client also sends JSON data to the server
- No backwards compatibility with old v2 clients
- More stability, fewer bugs, safer


## Next release?
v1.12 will probably be released in June - July, in the period from April - May v1.11.1 will be released at most.
I don't have time for another 'big' release due to some personal things that are more important, so June at the earliest

**Full Changelog**: https://github.com/Strawberry-Foundations/strawberry-chat/compare/v1.9.0...v1.11.0

*A big thank you to @Paddyk45 for helping with the development for v1.11.0 - without you none of this would have been possible.*
*Released by @Juliandev02*
