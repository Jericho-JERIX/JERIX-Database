import sqlite3

db = sqlite3.connect('./data/JerichoMessage.db')
Message = db.cursor()

res = Message.execute("SELECT * FROM Message")
for i in res:
    print(i)

db.close()