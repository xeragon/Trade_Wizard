import sqlite3

con = sqlite3.connect("bot_db.db")
cur = con.cursor()
# con.execute("PRAGMA foreign_keys = ON")
# cur.execute("CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY NOT NULL)")
# cur.execute("INSERT INTO users VALUES (1)")

# Uncomment the next line if you want to insert another user with uid 3
# cur.execute("INSERT INTO users VALUES (3)")

# cur.execute("CREATE TABLE IF NOT EXISTS binder (card TEXT NOT NULL, nb_card INT NOT NULL, uid INT NOT NULL, searching BOOLEAN NOT NULL, FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE)")
# Corrected the uid value in the INSERT statement to match the type (INTEGER)
# cur.execute("INSERT INTO binder VALUES ('just_a_card', 32, 9, 0)")

con.commit()
t = cur.execute("SELECT card from binder")
temp = t.fetchone()
print(temp)

    