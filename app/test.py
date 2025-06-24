from workTools.WorkWithDB import WorkWithDB

db = WorkWithDB.load_all()

for i in db.keys():
    print(i)
print(db.keys())