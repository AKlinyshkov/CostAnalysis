import sqlite3
from .dbmain import Purchase, Category, DBWork


class DBSqlite(DBWork):

    def __init__(self, path: str) -> None:
        self.dbconn = sqlite3.connect(path)
        self._pur_count = 0
        cursor = self.dbconn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM purchases')
            self.pur_count = cursor.fetchone()[0]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()

    # ==============================================================
    # Work with purchases count
    # ==============================================================

    @property
    def pur_count(self) -> int:
        return self._pur_count

    @pur_count.setter
    def pur_count(self, value):
        self._pur_count = value

    # ==============================================================
    # Select data
    # ==============================================================

    # ======================== Purchase ============================

    async def select_purchase_item(self, id_: int) -> Purchase | None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f'SELECT * FROM purchases WHERE id = {id_}')
            pur = cursor.fetchone()
            purchase = None if pur is None else Purchase(
                id_=pur[0],
                date=pur[1],
                product=pur[2],
                desc=pur[3],
                cost=pur[4],
                sum_=pur[5]
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return purchase

    async def select_all_purchases(self) -> list[Purchase]:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute('SELECT id, date(date), product, description, cost, sum '
                           'FROM purchases ORDER BY date')
            purs = cursor.fetchall()
            all_purchases = [
                Purchase(
                    id_=pur[0],
                    date=pur[1],
                    product=pur[2],
                    desc=pur[3],
                    cost=pur[4],
                    sum_=pur[5]
                ) for pur in purs
            ]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_purchases

    async def select_page_purchases(self, page_num: int, row_per_page: int) -> list[Purchase]:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute("SELECT id, date(date), product, description, cost, sum "
                           "FROM purchases ORDER BY date "
                           f"LIMIT {page_num * row_per_page}, {row_per_page}")
            purs = cursor.fetchall()
            all_purchases = [
                Purchase(
                    id_=pur[0],
                    date=pur[1],
                    product=pur[2],
                    desc=pur[3],
                    cost=pur[4],
                    sum_=pur[5]
                ) for pur in purs
            ]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_purchases

    # ======================== Category ============================

    async def select_all_categories(self) -> list[Category]:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute('SELECT * FROM categories')
            categories = cursor.fetchall()
            all_categories = [
                Category(category=cat[0],
                         product=cat[1],
                         hint=cat[2],
                         id_=cat[3]) for cat in categories]
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
            category = None if cat is None else Category(
                category=cat[0],
                product=cat[1],
                hint=cat[2],
                id_=cat[3])
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return category

    async def select_page_categories(self, page_num: int, row_per_page: int) -> list[Category]:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute("SELECT * "
                           "FROM categories ORDER BY category "
                           f"LIMIT {page_num * row_per_page}, {row_per_page}")
            cats = cursor.fetchall()
            all_categories = [
                Category(
                    category=cat[0],
                    product=cat[1],
                    hint=cat[2],
                    id_=cat[3]
                ) for cat in cats
            ]
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        return all_categories

    # ==============================================================
    # Insert Delete Update
    # ==============================================================

    # ======================== Purchase ============================

    async def insert_into_purchases(self, purchase: Purchase) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                "INSERT INTO purchases (date, product, description, cost, sum) "
                f"VALUES(date('{purchase.date}'), '{purchase.product}', "
                f"'{purchase.desc}', '{purchase.cost}', '{purchase.sum_}')"
            )
            self._pur_count += 1
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def delete_from_purchases(self, id_: int) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f'DELETE FROM purchases WHERE id = {id_}')
            self._pur_count -= 1
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def update_purchases(self, purchase: Purchase) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                "UPDATE purchases "
                f"set date = date('{purchase.date}'), "
                f"product = '{purchase.product}', "
                f"description = '{purchase.desc}', "
                f"cost = '{purchase.cost}', "
                f"sum = '{purchase.sum_}' "
                f"where id = {purchase.id_}"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    # ======================== Category ============================

    async def insert_into_categories(self, category: Category) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (category, product, hint) "
                f"VALUES('{category.category}', '{category.product}', '{category.hint}')"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def update_categories(self, category: Category) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(
                "UPDATE categories "
                f"set category = '{category.category}', "
                f"product = '{category.product}', "
                f"hint = '{category.hint}' "
                f"where id = {category.id_}"
            )
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()

    async def delete_from_categories(self, id_: int) -> None:
        cursor = self.dbconn.cursor()
        try:
            cursor.execute(f'DELETE FROM categories WHERE id = {id_}')
        except Exception as exp:
            raise exp
        finally:
            cursor.close()
        self.dbconn.commit()