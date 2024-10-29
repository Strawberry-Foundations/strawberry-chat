pub const CONNECTED: &str           = "%s has connected";
pub const DISCONNECTED: &str        = "%s has disconnected";
pub const ADDRESS_LEFT: &str        = "%s has left";
pub const USER_LEFT: &str           = "%s (%s) has left";
pub const QUEUE_KICK: &str          = "%s got kicked out of the queue";
pub const QUEUE_LEFT: &str          = "%s (%s) left the queue";
pub const QUEUE_JOIN: &str          = "%s (%s) is now in the queue";
pub const CONNECTED_RLM: &str       = "%s (ratelimited) has connected";
pub const LOGIN: &str               = "%s (%s) logged in";
pub const LOGIN_ERROR: &str         = "A login error with %s occurred!";
pub const CLIENT_UNAME_EMPTY: &str  = "Client username was empty";
pub const LOGIN_FAIL_CLOSED: &str   = "Failed to log in %s, connection closed to client";
pub const COMMUNICATION_ERROR: &str = "A communication error with %s (%s) occurred!";
pub const CONNECTION_ERROR: &str    = "A connection error occurred!";
pub const TRANSMISSION_ERROR: &str  = "A message transmission error occurred.";
pub const SQL_ERROR: &str           = "An SQL error occurred!";
pub const CLIENT_SIDE_ERROR: &str   = "A client-side error occurred.";
pub const S2C_ERROR: &str           = "A server-to-client exception occurred";
pub const REGISTRATION_ERROR: &str  = "A registration exception occurred";
pub const INVALID_SESSIONS_W: &str  = "You should kick some invalid sessions.";
pub const REM_INVALID_SESSION: &str = "Removed some invalid sessions.";
pub const BROADCAST_ERROR: &str     = "A broadcasting error occurred.";
pub const RUNTIME_STOP: &str        = "Runtime has stopped.";
pub const SERVER_STOP: &str         = "Server stopped";
pub const BADGE_ERROR: &str         = "Something went wrong while... doing something with the badges?: ";
pub const RATELIMIT_REMOVED: &str   = "Ratelimit timeout for %s removed";
pub const REACHED_CON_LIMIT: &str   = "IP address %s has reached its connection limit. Blocking IP address";
pub const CLIENT_KICKED: &str       = "%s was kicked. Reason: %s";

pub const DATABASE_CONNECTION_ERROR: &str = "Couldn't connect to database: %s";

pub const READ_PACKET_FAIL: &str = "Failed to read packet";
pub const WRITE_PACKET_FAIL: &str = "Failed to write packet";
pub const WRITE_STREAM_FAIL: &str = "Failed to write to stream";

pub const SEND_INTERNAL_MESSAGE_FAIL: &str  = "Failed to send internal message";