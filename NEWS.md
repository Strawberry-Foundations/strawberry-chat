
# v1.6.0
- NEW: AFK user list command
- NEW: Sending messages in Afk status is no longer possible
- NEW: AFK status stays even when you leave the chat
- NEW: Kickall command kicking all online users
- NEW: Changed Chat Name from Salware Chat to Strawberry Chat
- FIX: Fixed general formatting errors

# v1.7.0
- NEW: Bots are here!
       You can now create and program your own bots - so
       you can create your own commands, independent of the server! 
- NEW: User Profiles are here! You can now link your discord, write something 
       about yourself in your description or take a look at your fantastic badges!
- NEW: You can now create an account from the login page!
- NEW: Fancy User Chat Badges and exclusive badges for your user profile!
- NEW: Blacklisted Words + Set/Get/Add/Reload Command for Admins
- NEW: Character Limit with some special "easter eggs" :)
- NEW: User Nicknames and command to change your nickname
- NEW: Member Command to show registered users
- NEW: User info command to show information about a user
- NEW: New general messages with chat color support & more
- NEW: A new bot api for bots is comming to Strawberry Chat!
- ADMIN: Broadcast Command, Mute Command, Role set/get/color Command, Badge set/... Command nick set Command and Ban Command
- FIX: Fixed many many bugs
-> For more information visit https://github.com/orgs/Strawberry-Foundations/projects/1/views/1

# v1.7.1
- NEW: Modular code for better code structure
-> For more information visit https://github.com/orgs/Strawberry-Foundations/projects/1/views/1

# v1.8.0
- NEW: Memberlist command with beautiful representation of registered members and their roles
- NEW: We added direct messages to send private messages to a specific member instead of sending them to everyone.
- NEW: Updated user info command with Strawberry ID/Network intregation and online/offline status information
- NEW: Hashtag Placeholder Format (HTPF) for chat messages and broadcast command, to send colorized messages or the current time (e.g. #today)
- NEW: NEW: Added user mentioning, so if you mention a user (e.g. @someuser), it will be highlighted
- NEW: Working Kick command
- NEW: Added account creation date to user profile
- NEW: User settings command to manage user flags
- NEW: Reworked command system
- FIX: Fixed duplicated code which led to formatting errors
-> For more information visit https://github.com/orgs/Strawberry-Foundations/projects/1/views/1

# 1.8.1:
- NEW: Improved kick command with leave message
- NEW: Improved Discord Bridge
- FIX: Fixed Bad File Descriptor when logging out (#49)
- FIX: Fixed 'Sometimes logs get spammed with empty messages after a user connected/disconnected' (#39)
- FIX: Completly (hopefully) fixed broken formatting of log messages in console (#45)
- FIX: Fixed showing 'None' as main badge in Memberlist when no main badge is set (#47)
- UPDATE: Scapi has been updated to v0.11.0 with some improvements

# 1.8.2
- FIX: Fixed Console Logger prints static time instead of the real time (#63)
- SCAPI: Full update of Scapi for the legacy release of Scapi 1.0.0 (stbmv1)

# 1.9.0:
- NEW: Improved and complete new communication system for a better user experience
- NEW: We added a new configuration for server admins, to configure the maximal amount of logged in users!
- NEW: We also added a queue system for users, so when the server is full, you'll join the queue ;)
- NEW: Added experimental user avatars for discord bridge and soon maybe Strawberry Network
- FIX: Fixed When using Ctrl + C in client, the server will crash (BrokenPipe) (#1)
- FIX: We have fixed some general bugs that we didn't notice. Read changelog for more information (#63, #72, #70)
- ADMIN: We added a new command for server admins to configure the server or just show the current configurations!
Have a look at https://developers.strawberryfoundations.xyz/ for more documentation about Strawberry Chat :)

# 1.10.0:
- NEW: We added a new way to chat with your best friend! You can now use /joindm for an better DM interface!
- NEW: We also added notifications for desktop users, so if they get mentioned, they instantly get an notification ;)
- NEW: You can now block users from sending you dm messages ith the help of our new /block command!
- NEW: We improved our security system - Ratelimiting & automatic session removal!