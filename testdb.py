import sqlite3

db = sqlite3.connect('./data/Homeworklist.db')
Message = db.cursor()

res = Message.execute(f"SELECT id FROM Channel WHERE id = '885898083295186945'").fetchone()
print(res)
db.commit()

# if res:
#     print("Found",res[0])
# else:
#     print("Not Found")

db.close()