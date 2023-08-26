# Errorcodes
(C) = Client only error \
(S) = Server only error

* 001 = Connection error, client cannot connect correctly to the server (C)
* 002 = Login Error, something gone wrong while logging in
* 003 = Communication error, server could not send a message to client (S)
* 004 = Client-side error, server could not handle the request that the client send (C)
* 096 = SQL Error (S)
* 100 = General error
* 122 = BrokenPipe error, you may need to restart your server. Syncronization between server and client got interrupted
* 999 = Banned from the server (C)
