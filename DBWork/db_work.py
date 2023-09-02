import sqlite3
import asyncio
from dataclasses import dataclass


@dataclass
class Purchase:
    """
    date: str
    product: str
    cost: float
    sum_: float
    id_: int = 0
    """
    date: str
    product: str
    cost: float
    sum_: float
    id_: int = 0


@dataclass
class Category:
    """
    product: str
    category: str
    """
    product: str
    category: str


class DBWork:

    def __init__(self, path: str) -> None:
        self.dbconn = sqlite3.connect(path)

    # ==============================================================
    # Select data
    # ==============================================================

    async def select_purchase_item(self, id_: int) -> Purchase | None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f'SELECT * FROM purchases WHERE id = {id_}')
            pur = cursor.fetchone()
            purchase = Purchase(id_=pur[0], date=pur[1], product=pur[2], cost=pur[3], sum_=pur[4])
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return purchase

    async def select_all_purchases(self) -> list[Purchase] | None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute('SELECT id, date(date), product, cost, sum FROM purchases')
            purs = cursor.fetchall()
            all_purchases = [
                Purchase(
                    id_=pur[0],
                    date=pur[1],
                    product=pur[2],
                    cost=pur[3],
                    sum_=pur[4]
                ) for pur in purs
            ]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_purchases

    async def select_all_categories(self) -> list[Category] | None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute('SELECT * FROM categories')
            categories = cursor.fetchall()
            all_categories = [Category(product=cat[0], category=cat[1]) for cat in categories]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_categories

    async def select_category_by_product(self, product: str) -> Category | None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f"SELECT * FROM categories WHERE product = '{product}'")
            cat = cursor.fetchone()
            category = Category(product=cat[0], category=cat[1])
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return category

    # ==============================================================
    # Insert Delete Update
    # ==============================================================

    async def insert_into_purchases(self, purchase: Purchase) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                'INSERT INTO purchases (date, product, cost, sum) '
                f"VALUES(date('{purchase.date}'), '{purchase.product}', "
                f"'{purchase.cost}', '{purchase.sum_}')"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def delete_from_purchases(self, id_: int) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f'DELETE FROM purchases WHERE id = {id_}')
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def update_purchases(self, purchase: Purchase) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                'UPDATE purchases '
                f"set date = date('{purchase.date}'), "
                f"product = '{purchase.product}', "
                f"cost = '{purchase.cost}', "
                f"sum = '{purchase.sum_}' "
                f"where id = {purchase.id_}"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def insert_into_categories(self, category: Category) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categories(product, category) '
                f"VALUES('{category.product}', '{category.category}')"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()
