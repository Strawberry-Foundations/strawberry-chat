<div align="center">
  <h1>
    <a href="https://strawberryfoundations.xyz/strawberry-chat">Strawberry Chat</a>
    💬
  <h1>
  The universal chatting platform for (not just) your terminal!
  <br><br>

  ![Latest Stable Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.stable&label=Latest%20Stable%20Release&color=success)
  ![Latest Development Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.dev&label=Latest%20Development%20Release&color=cyan)
  ![Latest Canary Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.canary&label=Latest%20Canary%20Release&color=yellow)

  ![Codename](https://img.shields.io/badge/Codename-Vanilla_Cake_Rusty-orange)
  ![Code Size](https://img.shields.io/github/languages/code-size/Strawberry-Foundations/strawberry-chat)
  ![Commit activity](https://img.shields.io/github/commit-activity/w/Strawberry-Foundations/strawberry-chat)

</div>


## What is Strawberry Chat?
Strawberry Chat is a simple chat platform based on Rust Async Tcp Streams. It allows you to chat with other people in a simple and minimal way - without annoying tracking and spying.<br>
Also don't mind looking at our documentation! https://developers.strawberryfoundations.xyz/

## Why?
I wanted to program a "small" chat app because I had always been interested in microcomputing and bare bone technologies such as pure Tcp sockets. At the time I started, I only knew Python. Due to the size and features of Strawberry Chat, Strawberry Chat was rewritten in a faster and safer language, Rust. Strawberry Chat is not intended to be a replacement for conventional chat platforms - it is more of an addition to have fun. 

## How does Strawberry Chat work?
I can't explain everything in detail now, it might end up in our [Developer documentation](https://developers.strawberryfoundations.xyz/), but Strawberry Chat works by simply communicating via Tcp sockets - similar to IRC, except we have our own transport format. <br>
In the beginning, communication only took place via pure strings (if you can read German, [this](https://developers.strawberryfoundations.xyz/german/json-communication/introduction#versionen-des-strawberry-communication-standards) might be helpful). This was quite simple, but it limited the users very much. And so the [Strawberry Communication Standard](https://developers.strawberryfoundations.xyz/json-communication/introduction) was born.<nr>
With v2 of the standard, we implemented JSON to provide more options for how the client can represent a message. We are currently developing v3, which goes in both directions - server & client send JSON. 

## Security
Security is an important part when it comes to internet programs. As of January 30, 2024, there is still NO password hashing for the Rust rewrite.
In the following table you can see our security features and the corresponding versions:

| Version | Password Hashing  | TLS | Automoderation | IP Blocking | Ratelimit | Login Verification | Msg Verification | 
|---------|-------------------|-----|----------------|-------------|-----------|--------------------|------------------|
| `v1.8`  | ✅                | ❌  | ➖             | ❌          | ❌        | ❌                 | ❌               |
| `v1.9`  | ✅                | ❌  | ➖             | ❌          | ❌        | ❌                 | ❌               |
| `v1.10` | ✅                | ❌  | ➖             | ✅          | ✅        | ❌                 | ❌               |
| `v1.11` | ❌                | ❌  | ✅             | ✅          | ✅        | ✅                 | ✅               |

**Legend**
| ✅        | ❌            | ➖                    | 
|-----------|---------------|-----------------------|
| Supported | Not supported | Particially supported |

## Side Notes
### Config
Copy `./example.config.yml` to `./target/{RELEASE_TYPE}/config.yml` (Or to the same directory as the executable) 
and change values as needed