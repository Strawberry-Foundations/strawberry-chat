<div align="center">
  <h1>
    <a href="https://strawberryfoundations.org/strawberry-chat">Strawberry Chat</a> 💬<br>
    <h4><i>„If it has electricity, it can run Strawberry Chat“</i></h4>
  </h1>
  <h3>The universal chatting platform for (not just) your terminal!</h3>
  <br><br>

![Latest Stable Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.stable&label=Latest%20Stable%20Release&color=success)
![Latest Development Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.dev&label=Latest%20Development%20Release&color=cyan)
![Latest Canary Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.org/v1/versions&query=%24.stbchat.server.canary&label=Latest%20Canary%20Release&color=yellow)

![Codename](https://img.shields.io/badge/Codename-Rusty_Cake-orange)
![Code Size](https://img.shields.io/github/languages/code-size/Strawberry-Foundations/strawberry-chat)
![Commit activity](https://img.shields.io/github/commit-activity/w/Strawberry-Foundations/strawberry-chat)

</div>


## What is Strawberry Chat?
Strawberry Chat is a simple chat platform based on Rust Async Tcp Streams.
It allows you to chat with other people in a simple and minimal way - without annoying tracking and spying.<br>
Also don't mind looking at our documentation! https://developers.strawberryfoundations.org/

### Why?
I wanted to program a “small” chat application because I had always been interested in networking and simple technologies like pure Tcp sockets.
At the time I started, I only knew Python. Due to the scope and features of Strawberry Chat, Strawberry Chat was rewritten in a faster and safer language, Rust.
Strawberry Chat is not meant to be a replacement for traditional chat platforms - it's more of an addition to have fun.

## How does Strawberry Chat work?
Strawberry Chat uses TCP streams and a self-implemented JSON communication format.
For data compression [msgpack](https://msgpack.org/) is used.
There is a server and clients.
The processing of all data, commands, etc. takes place on the server - the client only serves as an input between server and client.

## Client
Our official [Strawberry Chat Client](https://github.com/Strawberry-Foundations/strawberry-chat-client) is best optimized for use with the official Strawberry Chat Server.
It is very easy to use and offers a configuration to save servers as well as credentials

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


# How to install
Strawberry Chat can be downloaded as a stable release [here](https://github.com/Strawberry-Foundations/strawberry-chat/releases/latest),
or as a development version directly from GitHub. However, this must be compiled manually.

### Config
When you start Strawberry Chat for the first time, Strawberry Chat automatically creates a configuration for you.
However, if you want to create a config file beforehand, you can copy the example.config.yml from this repository and modify it:
Copy `./example.config.yml` to `./target/{RELEASE_TYPE}/config.yml` (Or to the same directory as the executable)
and change values as needed

### Database
Strawberry Chat uses MySQL / MariaDB as database backend. The configuration for this is in the config.yml under the `database` section
The database needs a `users` table for Strawberry Chat to work

## Release cycle
We have developed the release schedule of Strawberry Chat so that a new version should be released every month.
This could be a major release (e.g. v1.12.0) or an intermediate release (e.g. v1.12.1).
Usually a major version is always followed by a minor version or an intermediate version.
In certain cases, 2 major or minor major versions can also be released in succession.

> [!NOTE]
> Due to a lack of ideas for new functions, this schedule cannot be adhered to.