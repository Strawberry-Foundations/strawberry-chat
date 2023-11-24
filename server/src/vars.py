from .colors import *

# Version-specified Variables & important variables
base_ver                = "1.8.2"
short_ver               = "1.8.2"
full_ver                = "v" + short_ver
update_channel          = "stable"
ver                     = short_ver + "-vacakes"
chat_name               = "Strawberry Chat"
codename                = "Vanilla Cake"
server_edition          = "Standard Edition"
authors                 = ["Juliandev02", "matteodev8", "Paddyk45"]
api                     = "http://api.strawberryfoundations.xyz/v1/"
sid_api                 = "https://id.strawberryfoundations.xyz/v1"

# SQL table query
table_query = """
    CREATE TABLE "users" (
	"user_id"	INTEGER,
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
	"msg_count"	INTEGER,
    "creation_date"	INTEGER)"""
 
role_colors = ["red", "green", "cyan", "blue", "yellow", "magenta",
               "lightred", "lightgreen", "lightcyan", "lightblue", "lightyellow", "lightmagenta",
               "boldred", "boldgreen", "boldcyan", "boldblue", "boldyellow", "boldmagenta"]

# Help Sections 
default_help_section    = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Default commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/help: {RESET}Help Command
        {BLUE + Colors.BOLD}/about: {RESET}About {chat_name}
        {BLUE + Colors.BOLD}/dm <user> <message>: {RESET}Send a private message to <user>
        {BLUE + Colors.BOLD}/news: {RESET}Newsletter
        {BLUE + Colors.BOLD}/exit, /quit: {RESET}Leave chat
        {BLUE + Colors.BOLD}/clientinfo: {RESET}Get some information about you
        {BLUE + Colors.BOLD}/shrug: {RESET}¯\_(ツ)_/¯
        {BLUE + Colors.BOLD}/tableflip: {RESET}(╯°□°)╯︵ ┻━┻
        {BLUE + Colors.BOLD}/unflip: {RESET}┬─┬ノ( º _ ºノ)
        {BLUE + Colors.BOLD}/server-info, /info: {RESET}Shows a description about this server \o/
    """
    
user_help_section       = f"""{CYAN + Colors.UNDERLINE + Colors.BOLD}Profile & User Commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/online: {RESET}Shows online users
        {BLUE + Colors.BOLD}/members, /users: {RESET}Shows registered users
        {BLUE + Colors.BOLD}/memberlist, /userlist: {RESET}Displays a list of members with their badges and roles
        {BLUE + Colors.BOLD}/user, /member <user>/me: {RESET}Shows information about the specified user
        {BLUE + Colors.BOLD}/nick <nickname/remove>: {RESET}Changes nickname to <nickname> or removes it
        {BLUE + Colors.BOLD}/description <desc>: {RESET}Set your user description
        {BLUE + Colors.BOLD}/badge set <badge>: {RESET}Sets your main badge
        {BLUE + Colors.BOLD}/discord <discord_uname>: {RESET}Set your discord username
        {BLUE + Colors.BOLD}/afk: {RESET}Toggle afk status
        {BLUE + Colors.BOLD}/unafk: {RESET}Untoggle afk status
        {BLUE + Colors.BOLD}/afks, /afklist: {RESET}Shows afk users
        {BLUE + Colors.BOLD}/msgcount: {RESET}Shows the number of messages you have written
    """
    
admin_help_section      = f"""{MAGENTA +  Colors.UNDERLINE + Colors.BOLD}Admin commands{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/kick <user> (<reason>): {RESET}Kick the specificed user for the (optionally) provided reason
        {BLUE + Colors.BOLD}/ban <user>: {RESET}Bans the specificed user
        {BLUE + Colors.BOLD}/unban <user>: {RESET}Unbans the specificed user     
        {BLUE + Colors.BOLD}/mute <user>: {RESET}Mutes the specificed user
        {BLUE + Colors.BOLD}/unmute <user>: {RESET}Unmutes the specificed user
        {BLUE + Colors.BOLD}/broadcast <message>: {RESET}Broadcast a message
        {BLUE + Colors.BOLD}/role get/set <user> (<role>) [<color>]: {RESET}Gets or sets the role of a user
        {BLUE + Colors.BOLD}/role color <user> <color>: {RESET}Gets or sets the role of a user
        {BLUE + Colors.BOLD}/nick set <username> <nickname/remove>: {RESET}Changes <user>'s nickname to <nickname> or removes it
        {BLUE + Colors.BOLD}/badge set <badge> <user>: {RESET}Changes main badge of <user> to <badge>
        {BLUE + Colors.BOLD}/badge add <badge> (<user>): {RESET}Adds new badge to your profile or to <user>'s profile
        {BLUE + Colors.BOLD}/bwords set/get <user> (<true/false>): {RESET}Enable or disable whether a user should be affected by the bad words
        {BLUE + Colors.BOLD}/bwords reload: {RESET}Reloads all blacklisted words
        {BLUE + Colors.BOLD}/bwords add <word>: {RESET}Adds a blacklisted word
        {BLUE + Colors.BOLD}/debug: {RESET}View debug informations
        {BLUE + Colors.BOLD}/kickall: {RESET}Kick all users (Currently not working)
    """
    
stbchatplus_help_section    = f"""{RED +  Colors.UNDERLINE + Colors.BOLD}Strawberry Chat+ commands & features{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}Still nothing here? {RESET}Check back another time!{RESET + Colors.RESET}
    """
    

user_settings_help          = f"""{CYAN + Colors.UNDERLINE + Colors.BOLD}User Settings{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/settings help: {RESET}Help Command
        {BLUE + Colors.BOLD}/settings enable_dms <true/false>: {RESET}Enable or disable your dms
        {BLUE + Colors.BOLD}/settings discord_name <discord_name>: {RESET}Change your discord name
        {BLUE + Colors.BOLD}/settings role_color <color>: {RESET}Change your role color
            -> Available Colors: <(light/bold)><red/green/cyan/blue/yellow/magenta>
        {BLUE + Colors.BOLD}/settings badge <badge>: {RESET}Sets your main badge
        {BLUE + Colors.BOLD}/settings description <description>: {RESET}Sets your description
        {BLUE + Colors.BOLD}/settings account username <new username>: {RESET}Change your current username
        {BLUE + Colors.BOLD}/settings account password <new password>: {RESET}Change your current password
    """
    
admin_settings_help          = f"""{MAGENTA +  Colors.UNDERLINE + Colors.BOLD}Admin Settings{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}/admin help: {RESET}Help Command
        {BLUE + Colors.BOLD}/admin enable_dms <username> <true/false>: {RESET}Enable or disable <username>'s dms
        {BLUE + Colors.BOLD}/admin enable_blacklisted_words <username> <true/false>: {RESET}Enable/disable if <username>'s is affected by bad words
        {BLUE + Colors.BOLD}/admin account_enabled <username> <true/false>: {RESET}Enable/disable <username>'s account
        
        {BLUE + Colors.BOLD}/admin discord_name <username> <discord_name>: {RESET}Change <username>'s discord name
        {BLUE + Colors.BOLD}/admin role_color <username> <color>: {RESET}Change <username>'s role color
            -> Available Colors: <(light/bold)><red/green/cyan/blue/yellow/magenta>
        {BLUE + Colors.BOLD}/admin badge <username> <badge>: {RESET}Sets <username>'s main badge
        {BLUE + Colors.BOLD}/admin description <username> <description>: {RESET}Sets <username>'s description
        {BLUE + Colors.BOLD}/admin role <username> <role>: {RESET}Sets <username>'s role
    """
    
server_help_section    = f"""  {GREEN +  Colors.UNDERLINE + Colors.BOLD}Server commands{RESET + Colors.RESET}
  {BLUE + Colors.BOLD}/help: {RESET}Help Command
  {BLUE + Colors.BOLD}/about: {RESET}About {chat_name}
  {BLUE + Colors.BOLD}/update: {RESET}Check for updates"""