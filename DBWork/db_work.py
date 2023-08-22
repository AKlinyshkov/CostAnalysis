"""
Errors:
Empty date or bad format - 1
Future date - 2
Empty product - 3
Bad product - 4
Empty cost/sum or bad format - 5
Cost/sum less then zero - 6
Bad/empty id - 7
No data found - 8
No corresponding category - 9
Bad category - 10
"""

import datetime
import re
import sqlite3


# ==============================================================
# Work with database
# ==============================================================


def create_db_connection(path: str) -> sqlite3.Connection:
	"""create database_connection"""

	dbconn = sqlite3.connect(path)
	return dbconn


# ==============================================================
# Select data
# ==============================================================

def select_pur_item(dbconn: sqlite3.Connection, id: int):
	"""select purchase item by id"""

	# Check ID
	try:
		check = int(id)
	except Exception:
		raise Exception(7, "Bad/empty id")
	
	try:
		cursor = dbconn.cursor()
		cursor.execute('SELECT * FROM purchases WHERE id = {}'.format(id))
		purchase = cursor.fetchone()
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	return purchase


def select_all_purchases(dbconn: sqlite3.Connection) -> list:
	"""show purchases table"""

	try:
		cursor = dbconn.cursor()
		cursor.execute('SELECT id, date(date), product, cost, sum FROM purchases')
		all_purchases = cursor.fetchall()
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	return all_purchases
	
	
def select_all_categories(dbconn: sqlite3.Connection) -> list:
	"""show categories table"""
	
	try:
		cursor = dbconn.cursor()
		cursor.execute('SELECT * FROM categories')
		all_categories = cursor.fetchall()
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	return all_categories
	

def select_category_by_product(dbconn: sqlite3.Connection, product: str):
	"""find category for product"""
	
	try:
		cursor = dbconn.cursor()
		cursor.execute("SELECT * FROM categories WHERE product = '{}'".format(product))
		category = cursor.fetchone()
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	
	return category



# ==============================================================
# Insert Delete Update
# ==============================================================


def insert_into_purchases(dbconn: sqlite3.Connection, date: str, product: str, cost: float, sum: float):
	"""insert into PURCHASES table"""
	
	# Check arguments

	#=====================================================
	if date == '':
		raise Exception(1, "Empty date or bad format")
	if product == '': 
		raise Exception(3, "Empty product")
	sum = sum if sum else cost
	if cost == '':
		raise Exception(5, "Empty cost/sum or bad format")
	
	#======================================================
	try:
		check = datetime.date.fromisoformat(date)
	except Exception:
		raise Exception(1, "Empty date or bad format")
	if datetime.date.fromisoformat(date) > datetime.date.today():
		raise Exception(2, "Future date")
	if not re.match(r'^\w+', product, flags=0):
		raise Exception(4, "Bad product")
	try:
		category = select_category_by_product(dbconn, product)
	except Exception:
		raise Exception(9, 'No corresponding category')
	try:
		check = float(cost); check = float(sum)
	except Exception:
		raise Exception(5, "Empty cost/sum or bad format")
	if (float(cost) < 0) or (float(sum) < 0):
		raise Exception(6, "Cost/sum less then zero")
	#======================================================

	try:
		cursor = dbconn.cursor()
		cursor.execute("INSERT INTO purchases (date, product, cost, sum) VALUES(date('{}'), '{}', '{}', '{}')".format(date, product, cost, sum))	  
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	dbconn.commit()


def delete_from_purchases(dbconn: sqlite3.Connection, id: int):
	"""delete from PURCHASES table"""
	
	# Check ID
	try:
		check = int(id)
	except Exception:
		raise Exception(7, "Bad/empty id")

	try:
		cursor = dbconn.cursor()
		cursor.execute('DELETE FROM purchases WHERE id = {}'.format(id))
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	dbconn.commit()
	

def update_purchases(dbconn: sqlite3.Connection, id: int, data: tuple):
	"""update PURCHASES"""

	date, product, cost, sum = data

	# Check ID
	try:
		check = int(id)
	except Exception:
		raise Exception(7, "Bad/empty id")
	
	#======================================================
	try:
		check = datetime.date.fromisoformat(date)
	except Exception:
		raise Exception(1, "Empty date or bad format")
	if datetime.date.fromisoformat(date) > datetime.date.today():
		raise Exception(2, "Future date")
	if not re.match(r'^\w+', product, flags=0):
		raise Exception(4, "Bad product")
	try:
		category = select_category_by_product(dbconn, product)
	except Exception:
		raise Exception(9, 'No corresponding category')
	try:
		check = float(cost); check = float(sum)
	except Exception:
		raise Exception(5, "Empty cost/sum or bad format")
	if (float(cost) < 0) or (float(sum) < 0):
		raise Exception(6, "Cost/sum less then zero")
	#======================================================
	
	try:
		cursor = dbconn.cursor()
		cursor.execute("UPDATE purchases set date = date('{}'), product = '{}', cost = '{}', sum = '{}' where id = {}".format(date, product, cost, sum, id))
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	dbconn.commit()
	
	
def insert_into_categories(dbconn: sqlite3.Connection, product: str, category: str):
	"""insert into CATEGORIES"""
	
	# Check category
	if not re.match(r'^\w+', category, flags=0):
		raise Exception(10, "Bad category")

	try:
		cursor = dbconn.cursor()
		cursor.execute("INSERT INTO categories(product, category) VALUES('{}', '{}')".format(product, category))
	except Exception as exp:
		raise exp
	finally:
		cursor.close()
	
	dbconn.commit()