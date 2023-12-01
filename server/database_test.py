from init import *

db = Database(driver="sqlite", database_path="./users.db")
print(db.fetch_all("SELECT nickname FROM users WHERE username = ?", ("Julian",)))