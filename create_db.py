import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

# MUST BE INTEGER
# This is the only place where int vs INTEGER matters—in auto-incrementing columns
create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username text, password text)"
cursor.execute(create_table)

admin_user='admin@deqree.in'
admin_pswd='deqree.in'

query="INSERT INTO users VALUES(NULL,'{}','{}')".format(admin_user,admin_pswd)
cursor.execute(query)

connection.commit()

connection.close()