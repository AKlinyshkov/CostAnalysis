import sqlite3

dbconn = sqlite3.connect('DB/expenses.db')
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
