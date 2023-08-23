import sqlite3
import sys
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication)


class SelectDBPath(QMainWindow):

    def __init__(self):
        super().__init__()
        self.path = QFileDialog.getExistingDirectory(self,"Select DB destination",".")

app = QApplication(sys.argv)
DBPath = SelectDBPath()

path = DBPath.path + "/expenses.db"

with open("DBWork/DBPath.txt", "w") as dbp:
    dbp.write(path)

dbconn = sqlite3.connect(path)
cur = dbconn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS categories (
   product text PRIMARY KEY,
   category text NOT NULL
);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS purchases (
   id INTEGER,
   date TEXT NOT NULL,
   product TEXT NOT NULL,   
   cost REAL NOT NULL,
   sum REAL NOT NULL,
   CONSTRAINT product_fk FOREIGN KEY (product) REFERENCES categories(product),
   CONSTRAINT purchases_pk PRIMARY KEY(id),
   CONSTRAINT product_not_null CHECK (product <> ''),
   CONSTRAINT cost_sum_upper_zero CHECK (cost > 0 and sum > 0)
);
""")

dbconn.commit()

dbconn.close()
