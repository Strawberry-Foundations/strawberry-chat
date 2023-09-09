# Version-specified Variables & important variables
base_ver                = "1.8.0"
short_ver               = "1.8.0b1+u3"
ver                     = short_ver + "-vacakes"
chat_name               = "Strawberry Chat"
codename                = "Vanilla Cake"
server_edition          = "Standard Edition"
authors                 = ["Juliandev02", "matteodev8", "Paddyk45"]
api                     = "http://api.strawberryfoundations.xyz/v1/"
table_query = """
    CREATE TABLE "users" (
	"user_id"	TEXT,
	"username"	TEXT,
	"password"	TEXT,
	"nickname"	INTEGER,
	"description"	TEXT,
	"badge"	TEXT,
	"badges"	TEXT,
	"role"	TEXT,
	"role_color"	TEXT,
	"enable_blacklisted_words"	TEXT,
	"account_enabled"	TEXT,
	"enable_dms"	TEXT,
	"muted"	TEXT,
	"strawberry_id"	TEXT,
	"discord_name"	TEXT,
	"msg_count"	INTEGER)"""