# [Strawberry Chat](https://github.com/orgs/Strawberry-Foundations/projects/1)
The universal chatting platform for your terminal!<br><br>
![Latest Stable Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.stable&label=Latest%20Stable%20Release&color=success)
![Latest Development Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.dev&label=Latest%20Development%20Release&color=success)
![Latest Canary Release](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.canary&label=Latest%20Canary%20Release&color=success)
![Codename](https://img.shields.io/badge/Codename-Vanilla_Cake-darkred)<br>
![Scapi Stable](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.scapi.bot.stable&label=Scapi%20Stable%20Release&color=blue)
![Scapi Development](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.scapi.bot.dev&label=Scapi%20Development%20Release&color=blue)
![Scapi Canary](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.scapi.bot.canary&label=Scapi%20Canary%20Release&color=blue) <br>
![Code Size](https://img.shields.io/github/languages/code-size/Strawberry-Foundations/strawberry-chat) ![Commit activity](https://img.shields.io/github/commit-activity/w/Strawberry-Foundations/strawberry-chat) ![License](https://img.shields.io/github/license/Strawberry-Foundations/strawberry-chat)<br> [![CodeQL](https://github.com/Strawberry-Foundations/strawberry-chat/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Strawberry-Foundations/strawberry-chat/actions/workflows/github-code-scanning/codeql) [![Python Application](https://github.com/Strawberry-Foundations/strawberry-chat/actions/workflows/python.yml/badge.svg)](https://github.com/Strawberry-Foundations/strawberry-chat/actions/workflows/python.yml) <br>

## What is Strawberry Chat?
Strawberry Chat is a simple chat platform based on Python TCP sockets. It allows you to chat with other people in a simple and minimal way - without annoying tracking and spying. 

## Why?
My goal was to develop a chat app for the terminal, which is not only minimal, but also useful. Strawberry Chat is actively developing and getting more and more features - and the best thing is, everything is free and stays free! 
In addition, Strawberry Chat is open source. This means that everyone can contribute to the project. Also, every user can create his own server if he/she wants to chat privately with his/her friends - we are happy about every single user and accept everyone with a warm heart! 

## [JSON Communication](https://github.com/Strawberry-Foundations/strawberry-chat/tree/json-communication)
Strawberry Chat is currently being rewritten so that we use JSON as the communication format. There are therefore compatibility problems between the server and client.
|  | v1.7.0 ![](https://img.shields.io/badge/Deprecated-red) | v1.8.0 ![](https://img.shields.io/badge/Stable-success) | v1.8.1 ![](https://img.shields.io/badge/Dev-cyan) | v1.9.0 ![](https://img.shields.io/badge/Canary-yellow) |
| -------------------------------------------------------------- | ------ | ------ | ------ | ------ |
| ![](https://img.shields.io/badge/Standard-<=v2.4.0-success)    | ✅    | ✅     | ✅    | ❌     |
| ![](https://img.shields.io/badge/Standard-v2.5.0-success)      | ❌    | ❌     | ❌    | ✅     |
| ![](https://img.shields.io/badge/Standard->=v2.5.1-success)    |✅ (CM)| ✅ (CM)|✅ (CM)| ✅     |
| ![](https://img.shields.io/badge/Lite-<=v1.0.1-success)        | ✅    | ✅     | ✅    | ❌     |
| ![](https://img.shields.io/badge/Lite->=v1.1.0-success)        | ❌    | ❌     | ❌    | ✅     |
| ![](https://img.shields.io/badge/Nano-<=v1.0.1-success)        | ✅    | ✅     | ✅    | ❌     |
| ![](https://img.shields.io/badge/Nano->=v1.1.0-success)        | ❌    | ❌     | ❌    | ✅     |
| ![](https://img.shields.io/badge/Berryjuice--pico-success)     | ✅    | ✅     | ✅    | ❌     |


<!-- > [!IMPORTANT]  
> As of Client Canary v2.5.1, we have added a feature that allows users to connect to old servers. This is called Compatiblity Mode. To activate it you either have to add `compatiblity_mode: true` to the respective legacy server entry or start the client with the `--compatiblity-mode` flag! -->

| CM (Compatiblity Mode)    | As of Client Canary v2.5.1, we have added a feature that allows users to connect to old servers. This is called Compatiblity Mode. To activate it you either have to add `compatiblity_mode: true` to the respective legacy server entry or start the client with the `--compatiblity-mode` flag! |
|---------------|:------------------------|



## Security
Strawberry Chat has now officially received password hashing with the release of version 1.8.0. We're using a secure hashing algorithm for the stored passwords. On weaker devices without cryptographic extensions (e.g. Raspberry Pi 4) you will notice that there is a slight delay when logging in. This is due to the hashing algorithm we use. Due to the high security, the system needs more time.  

## FaQ
**Q:** Can I create my own client?<br>
**A:** Yes, of course! As long as this client adheres to our terms of use (currently in progress), you may use and actively develop it! Just create a fork (You can also upload the client file individually in a separate GitHub repo, just please ask first if this is okay!), and edit the client file as it suits you! But please still adhere to our terms of use! :)

**Q:** Can I host my own server?<br>
**A:** Yes. Hosting your own servers is totally easy! You can even add your own commands for your friends or community, and change the texts as you like! Only if you upload this to GitHub or something else, you should please follow our terms of use and create a fork :) We would be happy if you would chat with us on the official chat server :) The user experience is much better there

### Clients
| Name                                                                                     | Type | Author                                                             | State                                                                                                                 | Version     |
|------------------------------------------------------------------------------------------| --   | --                                                                  | --                                                                                                                    | --                                              |             
| stbchat ![official](https://img.shields.io/badge/Official-success)                       | CLI  | [Strawberry-Foundations](https://github.com/Strawberry-Foundations) | ![state](https://img.shields.io/badge/Open--Source-success) ![state](https://img.shields.io/badge/Available-success)  | ![](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.client.stable&label=Stable&color=success) <br>![](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.client.canary&label=Canary&color=success)          |
| stbchat-lite ![official](https://img.shields.io/badge/Official-success)                  | CLI  | [Strawberry-Foundations](https://github.com/Strawberry-Fondations) | ![state](https://img.shields.io/badge/Open--Source-success)  ![state](https://img.shields.io/badge/Available-success) | ![version](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.client.lite&label=%20&color=success)       |
| stbchat-nano ![official](https://img.shields.io/badge/Official-success)                  | CLI  | [Strawberry-Foundations](https://github.com/Strawberry-Fondations) | ![state](https://img.shields.io/badge/Open--Source-success)  ![state](https://img.shields.io/badge/Available-success) | ![version](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.client.nano&label=%20&color=success)       |
| berryjuice (Former sprchrgd) ![friend](https://img.shields.io/badge/Good_Friend-magenta) | CLI  | [matteodev8](https://github.com/matteodev8)    | ![state](https://img.shields.io/badge/In_development_again-success) ![state](https://img.shields.io/badge/Currently_Not_Available-orange)      | ![version](https://img.shields.io/badge/v1.0.0deva-success) 
| [berryjuice-pico](https://gist.github.com/matteodev8/1150d4141c748c94386dedc4821f7ad7) ![friend](https://img.shields.io/badge/Good_Friend-magenta)          | CLI  | [matteodev8](https://github.com/matteodev8)            | ![state](https://img.shields.io/badge/Open--Source-success) ![state](https://img.shields.io/badge/Available-success) | ![version](https://img.shields.io/badge/staging-lightblue)

### Server
| Name                                                                             | Author                                                              | State                   | Version                                                                  |
| --                                                                     | --                                                        | --                      | --                                                                       |
| stbserver ![official](https://img.shields.io/badge/Official-success)  | [Strawberry-Foundations](https://github.com/Strawberry-Foundations) | ![state](https://img.shields.io/badge/Open--Source-success) ![state](https://img.shields.io/badge/Available-success)  | ![](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.stable&label=Stable&color=success) <br>![](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.dev&label=Dev&color=success) <br>![](https://img.shields.io/badge/dynamic/json?url=https://api.strawberryfoundations.xyz/v1/versions&query=%24.stbchat.server.canary&label=Canary&color=success)              |
| slfcserver ![official](https://img.shields.io/badge/Official-success) | [Strawberry-Foundations (Former Salware-Foundations)](https://github.com/Strawberry-Foundations) | ![version](https://img.shields.io/badge/Discontinued-orange) ![state](https://img.shields.io/badge/Available-success) | ![version](https://img.shields.io/badge/v1.2.0-orange)                   |

