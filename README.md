<div align="center">
  <h1>
    <a href="https://strawberryfoundations.org/strawberry-chat">Strawberry Chat</a>
    💬
  </h1>
  <h2>The universal chatting platform for (not just) your terminal!</h2>
  <br><br>

  ![Latest Stable Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.stable&label=Latest%20Stable%20Release&color=success)
  ![Latest Development Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.dev&label=Latest%20Development%20Release&color=cyan)
  ![Latest Canary Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.canary&label=Latest%20Canary%20Release&color=yellow)

  ![Codename](https://img.shields.io/badge/Codename-Rusty_Cake-orange)
  ![Code Size](https://img.shields.io/github/languages/code-size/Strawberry-Foundations/strawberry-chat)
  ![Commit activity](https://img.shields.io/github/commit-activity/w/Strawberry-Foundations/strawberry-chat)

</div>


## What is Strawberry Chat?
Strawberry Chat is a simple chat platform based on Rust Async Tcp Streams. It allows you to chat with other people in a simple and minimal way - without annoying tracking and spying.<br>
Also don't mind looking at our documentation! https://developers.strawberryfoundations.org/

## Why?
I wanted to program a "small" chat app because I had always been interested in microcomputer and bare-bones technologies such as pure Tcp sockets. At the time I started, I only knew Python. Due to the size and features of Strawberry Chat, Strawberry Chat was rewritten in a faster and safer language, Rust. Strawberry Chat is not intended to be a replacement for conventional chat platforms - it is more of an addition to have fun. 

## How does Strawberry Chat work?
I can't explain everything in detail now, it might end up in our [Developer documentation](https://developers.strawberryfoundations.org/), but Strawberry Chat works by simply communicating via Tcp sockets - similar to IRC, except we have our own transport format. <br>
In the beginning, communication only took place via pure strings (if you can read German, [this](https://developers.strawberryfoundations.org/german/json-communication/introduction#versionen-des-strawberry-communication-standards) might be helpful). This was quite simple, but it limited the users very much. And so the [Strawberry Communication Standard](https://developers.strawberryfoundations.org/json-communication/introduction) was born.<nr>
With v2 of the standard, we implemented JSON to provide more options for how the client can represent a message. We are currently developing v3, which goes in both directions - server & client send JSON. 

## Security
Security is an important part when it comes to internet programs.
In the following table you can see our security features and the corresponding versions:

| Version | PW Hashing | TLS | Auto-<br>mod | IP Block | Ratelimit | Login Verification | Msg Verification | Watchdog | 
|---------|------------|-----|--------------|----------|-----------|--------------------|------------------|----------|
| `v1.8`  | ✅          | ❌   | ➖            | ❌        | ❌         | ❌                  | ❌                | ❌        |
| `v1.9`  | ✅          | ❌   | ➖            | ❌        | ❌         | ❌                  | ❌                | ❌        |
| `v1.10` | ✅          | ❌   | ➖            | ✅        | ✅         | ❌                  | ❌                | ❌        |
| `v1.11` | ✅          | ❌   | ✅            | ✅        | ✅         | ✅                  | ✅                | ✅        |

**Legend**

| ✅         | ❌             | ➖                   | 
|-----------|---------------|---------------------|
| Supported | Not supported | Partially supported |


## Release cycle

We have developed the Strawberry Chat release schedule so that a version is released approximately every month.
This can be a major release (such as v1.9, v.11), but it can also be a minor release (such as v1.8.2).
In rare cases, a new version is only released every 2 months.

> The last stable release before v1.11.0 was released on December 1, 2023, and was version 1.9.0.
> About 5 months have passed since this release.
> In very rare cases this can happen. This was because we rewrote Strawberry Chat in a completely different language,
> namely Rust, which takes a lot of time. We do not plan to change the language in the future - however,
> if we change anything in our code base, which could take a long time,
> it is quite possible that the release of a new version could take several months.


## Side Notes
### Config
When you start Strawberry Chat for the first time, Strawberry Chat automatically creates a configuration for you.
However, if you want to create a config file beforehand, you can copy the example.config.yml from this repository and modify it:
Copy `./example.config.yml` to `./target/{RELEASE_TYPE}/config.yml` (Or to the same directory as the executable) 
and change values as needed