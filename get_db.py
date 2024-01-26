class getDB:
    def __init__(self):
        self.ip = ""
        self.username = ""
        self.db_name = ""
        self.pwd = ""
        self.port = 3306
        self.read_file()

    def read_file(self):
        # print(path.parent.absolute())
        with open("sql.txt" , "r") as f:
            db = f.readlines()
            self.ip = db[0].strip()
            self.username = db[1].strip()
            self.pwd = db[2].strip()
            self.db_name = db[3].strip()
            self.port = db[4].strip()

if __name__ == "__main__":
    db = getDB()
    print(db.ip)