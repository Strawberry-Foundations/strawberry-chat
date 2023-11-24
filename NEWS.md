# v1.6.0
- NEW: AFK user list command
- NEW: Sending messages in Afk status is now not possible
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
- NEW: New communication system for a better user experience
- NEW: We added a new configuration for server admins, to configure the maximal amount of logged in users!
- NEW: We also added a queue system for users, so when the server is full, you'll join the queue ;)