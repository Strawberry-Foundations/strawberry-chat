# Errorcodes
(C) = Client only error \
(S) = Server only error

* 001 = Connection error, client cannot connect correctly to the server (C)
* 002 = Login Error, something gone wrong while logging in
* 003 = Communication error, server could not send a message to client (S)
* 004 = Client-side error, server could not handle the request that the client send (C)
* 005 = Socket-to-Client error, Server and Client couldnt communicate correctly (Occurs often when trying to delete the user out of the online users) (C/S)
* 021 = Registration Error, something gone wrong while registrating a user
* 096 = SQL Error (S)
* 100 = General error
* 122 = BrokenPipe error, you may need to restart your server. Syncronization between server and client got interrupted
* 242 = message transmission error
* 999 = Banned from the server (C)
