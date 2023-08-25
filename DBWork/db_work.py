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


class DBWork:

	def __init__(self, path: str):
		self.dbconn = sqlite3.connect(path)


	# ==============================================================
	# Select data
	# ==============================================================

	def select_pur_item(self, id: int) -> tuple[int, str, str, float, float] | None:
		"""select purchase item by id"""
		
		try:
			cursor = self.dbconn.cursor()
			cursor.execute('SELECT * FROM purchases WHERE id = {}'.format(id))
			purchase = cursor.fetchone()
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		return purchase


	def select_all_purchases(self) -> list[tuple[int, str, str, float, float]] | None:
		"""show purchases table"""

		try:
			cursor = self.dbconn.cursor()
			cursor.execute('SELECT id, date(date), product, cost, sum FROM purchases')
			all_purchases = cursor.fetchall()
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		return all_purchases
		
		
	def select_all_categories(self) -> list[tuple[str,str]] | None:
		"""show categories table"""
		
		try:
			cursor = self.dbconn.cursor()
			cursor.execute('SELECT * FROM categories')
			all_categories = cursor.fetchall()
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		return all_categories
		

	def select_category_by_product(self, product: str) -> tuple[str, str] | None:
		"""find category for product"""
		
		try:
			cursor = self.dbconn.cursor()
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


	def insert_into_purchases(self, date: str, product: str, cost: float, sum: float) -> None:
		"""insert into PURCHASES table"""
		
		# Check arguments

		#=====================================================
		if date == '':
			raise Exception(1, "Empty date or bad format")
		if product == '': 
			raise Exception(3, "Empty product")
		sum = sum if sum else cost
		if cost is None:
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
			category = self.select_category_by_product(product)
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
			cursor = self.dbconn.cursor()
			cursor.execute("INSERT INTO purchases (date, product, cost, sum) VALUES(date('{}'), '{}', '{}', '{}')".format(date, product, cost, sum))	  
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		self.dbconn.commit()


	def delete_from_purchases(self, id: int) -> None:
		"""delete from PURCHASES table"""
		
		try:
			cursor = self.dbconn.cursor()
			cursor.execute('DELETE FROM purchases WHERE id = {}'.format(id))
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		self.dbconn.commit()
		

	def update_purchases(self, id: int, date: str, product: str, cost: float, sum: float) -> None:
		"""update PURCHASES"""

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
			category = self.select_category_by_product(product)
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
			cursor = self.dbconn.cursor()
			cursor.execute("UPDATE purchases set date = date('{}'), product = '{}', cost = '{}', sum = '{}' where id = {}".format(date, product, cost, sum, id))
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		self.dbconn.commit()
		
		
	def insert_into_categories(self, product: str, category: str) -> None:
		"""insert into CATEGORIES"""
		
		# Check category
		if not re.match(r'^\w+', category, flags=0):
			raise Exception(10, "Bad category")

		try:
			cursor = self.dbconn.cursor()
			cursor.execute("INSERT INTO categories(product, category) VALUES('{}', '{}')".format(product, category))
		except Exception as exp:
			raise exp
		finally:
			cursor.close()
		
		self.dbconn.commit()
