"""
Errors:
Empty date or bad format - 1
Empty product - 3
Empty cost/sum or bad format - 5
Cost/sum less then zero - 6
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

    def select_purchase_item(self, id_: int) -> tuple[int, str, str, float, float] | None:
        try:
            cursor = self.dbconn.cursor()
            cursor.execute(f'SELECT * FROM purchases WHERE id = {id_}')
            purchase = cursor.fetchone()
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return purchase

    def select_all_purchases(self) -> list[tuple[int, str, str, float, float]] | None:
        try:
            cursor = self.dbconn.cursor()
            cursor.execute('SELECT id, date(date), product, cost, sum FROM purchases')
            all_purchases = cursor.fetchall()
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_purchases

    def select_all_categories(self) -> list[tuple[str, str]] | None:
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
        try:
            cursor = self.dbconn.cursor()
            cursor.execute(f"SELECT * FROM categories WHERE product = '{product}'")
            category = cursor.fetchone()
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return category

    # ==============================================================
    # Insert Delete Update
    # ==============================================================

    def insert_into_purchases(self, date: str, product: str, cost: float, sum_: float) -> None:
        # =================== Data is not empty ================
        if date == '':
            raise Exception(1, "Empty date or bad format")
        if product == '':
            raise Exception(3, "Empty product")
        sum_ = sum_ if sum_ else cost
        if cost is None:
            raise Exception(5, "Empty cost/sum or bad format")

        # =================== Value validation =================
        try:
            datetime.date.fromisoformat(date)
        except Exception:
            raise Exception(1, "Empty date or bad format")
        if (float(cost) < 0) or (float(sum_) < 0):
            raise Exception(6, "Cost/sum less then zero")
        # ======================================================

        try:
            cursor = self.dbconn.cursor()
            cursor.execute(
                'INSERT INTO purchases (date, product, cost, sum) '
                f"VALUES(date('{date}'), '{product}', '{cost}', '{sum_}')"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    def delete_from_purchases(self, id_: int) -> None:
        try:
            cursor = self.dbconn.cursor()
            cursor.execute(f'DELETE FROM purchases WHERE id = {id_}')
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    def update_purchases(self, id_: int, date: str, product: str, cost: float, sum_: float) -> None:
        # =================== Data is not empty ================
        if date == '':
            raise Exception(1, "Empty date or bad format")
        if product == '':
            raise Exception(3, "Empty product")
        sum_ = sum_ if sum_ else cost
        if cost is None:
            raise Exception(5, "Empty cost/sum or bad format")

        # =================== Value validation =================
        try:
            datetime.date.fromisoformat(date)
        except Exception:
            raise Exception(1, "Empty date or bad format")
        if (float(cost) < 0) or (float(sum_) < 0):
            raise Exception(6, "Cost/sum less then zero")
        # ======================================================

        try:
            cursor = self.dbconn.cursor()
            cursor.execute(
                'UPDATE purchases '
                f"set date = date('{date}'), "
                f"product = '{product}', "
                f"cost = '{cost}', "
                f"sum = '{sum_}' "
                f"where id = {id_}"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    def insert_into_categories(self, product: str, category: str) -> None:
        # Check category
        try:
            cursor = self.dbconn.cursor()
            cursor.execute(
                'INSERT INTO categories(product, category) '
                f"VALUES('{product}', '{category}')"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()
