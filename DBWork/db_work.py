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
from sqlite3 import IntegrityError


# ==============================================================
# Exception processing
# ==============================================================

# Decorator check arguments no empty
def argsNoEmpty(func):
	def decorated(**kwargs):
		date, product, cost, sum = kwargs.get('data')
		if date == '':
			date = datetime.date.today().isoformat()
			kwargs['data'] = (date, product, cost, sum)
		if product == '': 
			raise Exception(3, "Empty product")
		sum = sum if sum else cost
		kwargs['data'] = (date, product, cost, sum)
		if cost == '':
			raise Exception(5, "Empty cost/sum or bad format")
		res = func(**kwargs)
		if res:
			return res
	return decorated
	
	
# Decorator check arguments value
def argsNoBad(func):
	def decorated(**kwargs):
		date, product, cost, sum = kwargs.get('data')
		try:
			check = datetime.date.fromisoformat(date)
		except Exception:
			raise Exception(1, "Empty date or bad format")
		if datetime.date.fromisoformat(date) > datetime.date.today():
			raise Exception(2, "Future date")
		if not re.match(r'^\w+', product, flags=0):
			raise Exception(4, "Bad product")
		try:
			dbconn = kwargs.get('dbconn')
			category = select_category_by_product(dbconn = dbconn, product = product)
		except Exception:
			raise Exception(9, 'No corresponding category')
		try:
			check = float(cost); check = float(sum)
		except Exception:
			raise Exception(5, "Empty cost/sum or bad format")
		if (float(cost) < 0) or (float(sum) < 0):
			raise Exception(6, "Cost/sum less then zero")
		res = func(**kwargs)
		if res:
			return res
	return decorated
	

# Decorator ID errors catching
def catchIDerror(func):
	def decorated(**kwargs):
		id = kwargs.get("id")
		try:
			check = int(id)
		except Exception:
			raise Exception(7, "Bad/empty id")
		res = func(**kwargs)
		if res:
			return res
	return decorated
	

# Decorator NoData errors catching
def catchNoDataerror(func):
	def decorated(**kwargs):
		res = func(**kwargs)
		if res:
			return res
		else:
			raise Exception(8, "No data found")
	return decorated


# Decorator check category arguments
def argsCategory(func):
	def decorated(**kwargs):
		product, category = kwargs.get('data')
		if not re.match(r'^\w+', category, flags=0):
			raise Exception(10, "Bad category")
		res = func(**kwargs)
		if res:
			return res
	return decorated




# ==============================================================
# Work with database
# ==============================================================

#create database_connection
def create_db_connection(path):
	dbconn = sqlite3.connect(path)
	return dbconn



# ==============================================================
# Select data
# ==============================================================

#select purchase item by id
@catchIDerror
@catchNoDataerror
def select_pur_item(**kwargs):
	dbconn = kwargs.get("dbconn")
	id = kwargs.get("id")
	cursor = dbconn.cursor()
	cursor.execute('SELECT * FROM purchases WHERE id = {}'.format(id))
	purchase = cursor.fetchone()
	cursor.close()
	return purchase

# show purchases table
@catchNoDataerror
def select_all_purchases(**kwargs):
	dbconn = kwargs.get("dbconn")
	cursor = dbconn.cursor()
	cursor.execute('SELECT id, date(date), product, cost, sum FROM purchases')
	all_purchases = cursor.fetchall()
	cursor.close()
	return all_purchases
	
	
# show categories table
@catchNoDataerror
def select_all_categories(**kwargs):
	dbconn = kwargs.get("dbconn")
	cursor = dbconn.cursor()
	cursor.execute('SELECT * FROM categories')
	all_categories = cursor.fetchall()
	cursor.close()
	return all_categories
	
# find category for product
@catchNoDataerror
def select_category_by_product(**kwargs):
	dbconn = kwargs.get("dbconn")
	product = kwargs.get("product")
	
	cursor = dbconn.cursor()
	try:
		cursor.execute("SELECT * FROM categories WHERE product = '{}'".format(product))
	except Exception as excp:
		print(excp.args)
	category = cursor.fetchone()
	cursor.close()
	
	return category



# ==============================================================
# Insert Delete Update
# ==============================================================

#insert into PURCHASES table
@argsNoEmpty
@argsNoBad
def insert_into_purchases(**kwargs):
	dbconn = kwargs.get("dbconn")
	date, product, cost, sum = kwargs.get("data")
	
	cursor = dbconn.cursor()
	cursor.execute("INSERT INTO purchases (date, product, cost, sum) VALUES(date('{}'), '{}', '{}', '{}')".format(date, product, cost, sum))	  
	cursor.close()
	dbconn.commit()

#delete from PURCHASES table
@catchIDerror
def delete_from_purchases(**kwargs):
	dbconn = kwargs.get("dbconn")
	id = kwargs.get("id")
	cursor = dbconn.cursor()
	cursor.execute('DELETE FROM purchases WHERE id = {}'.format(id))
	cursor.close()
	dbconn.commit()
	
# update PURCHASES
@catchIDerror
@argsNoBad
def update_purchases(**kwargs):
	dbconn = kwargs.get("dbconn")
	id = kwargs.get("id")
	data = kwargs.get("data")
	
	cursor = dbconn.cursor()
	cursor.execute("UPDATE purchases set date = date('{}'), product = '{}', cost = '{}', sum = '{}' where id = {}".format(data[0], data[1], data[2], data[3], id))
	cursor.close()
	dbconn.commit()
	
		
#insert into CATEGORIES
@argsCategory	
def insert_into_categories(**kwargs):
	dbconn = kwargs.get("dbconn")
	product, category = kwargs.get("data")
	
	cursor = dbconn.cursor()
	cursor.execute("INSERT INTO categories(product, category) VALUES('{}', '{}')".format(product, category))
	cursor.close()
	
	dbconn.commit()