from init import *

db = Database(driver="mysql", database_path="./users.db")
# print(db.fetch_all("SELECT username FROM users WHERE username = ?", ("Julian",)))
db._execute_query('INSERT INTO users (username, password, role, role_color, enable_blacklisted_words, account_enabled, muted, user_id, msg_count, enable_dms, creation_date) VALUES ("Julian", "test", "member", "red", "true", "true", "false", 0, 0, true, 1);')