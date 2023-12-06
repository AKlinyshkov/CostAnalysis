import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dbwork.dbmain import Purchase, Category, DBWork
from dbwork.dbsqlite import DBSqlite
import datetime
import re
import asyncio

rows_per_num = 10


# show purchases table
async def show_purchases(db: DBWork) -> None:
    page_count = (db.pur_count - 1) // rows_per_num + 1
    all_purchases = await db.select_page_purchases(page_count - 1, rows_per_num)
    print(
        '\n-------------------------------------------------------------------'
        '---------------------------------------------------------------------'
    )
    print(
        f'|  {"ID":<5}  |  {"Date":<10}  |  {"Product":<30}  |  {"Description":<40}  | '
        f' {"cost":<10}  |  {"sum":<10}  |')
    print(
        '|---------|--------------|----------------------------------|'
        '--------------------------------------------|--------------|--------------|'
    )
    if all_purchases:
        for purchase in all_purchases:
            print(
                f'|  {purchase.id_:<5}  |  {purchase.date:<10}  |  {purchase.product:<30}  '
                f'|  {purchase.desc:<40}  |  {purchase.cost:<10}  |  {purchase.sum_:<10}  |'
            )
        print(
            '--------------------------------------------------------------------'
            '--------------------------------------------------------------------\n'
        )


# insert into purchases table
async def insert_purchase(db: DBWork) -> None:
    print("Введите необходимые данные")
    date = input("Дата ({}): ".format(datetime.date.today()))
    date = date if date else str(datetime.date.today())
    product = input("Продукт: ")
    desc = input("Описание: ")
    cost = input("Цена: ")
    sum_ = input("Сумма (Enter, если равно цене): ")
    sum_ = sum_ if sum_ else cost
    await db.insert_into_purchases(
        Purchase(date=date, product=product, desc=desc, cost=float(cost), sum_=float(sum_))
    )


# delete from purchases table
async def delete_purchase(db: DBWork) -> None:
    await show_purchases(db)
    id = input("Введите id удаляемой покупки: ")

    p = re.compile('[\,| ]+')
    ids = p.sub(' ', id).split(' ')

    succ = []

    for id_ in ids:
        await db.delete_from_purchases(int(id_))
        succ.append(id_)

    await show_purchases(db)


# update purchases
async def update_purchase(db: DBWork) -> None:
    await show_purchases(db)
    id = str(input("Введите id изменяемой покупки: "))
    old_purchase = await db.select_purchase_item(int(id))

    print("Введите необходимые данные")
    if old_purchase:
        date = input("Дата ({}): ".format(old_purchase.date))
        product = input("Продукт ({}): ".format(old_purchase.product))
        desc = input("Описание ({}): ".format(old_purchase.desc))
        cost = input("Цена ({}): ".format(old_purchase.cost))
        sum_ = input("Сумма ({}): ".format(old_purchase.sum_))

        date = date if date else old_purchase.date
        product = product if product else old_purchase.product
        desc = desc if desc else old_purchase.desc
        cost = cost if cost else old_purchase.cost
        sum_ = sum_ if sum_ else old_purchase.sum_
    else:
        raise Exception("Purchase not found")

    await db.update_purchases(
        Purchase(
            id_=int(id),
            date=date,
            product=product,
            desc=desc,
            cost=float(cost),
            sum_=float(sum_))
    )

    await show_purchases(db)


# main function
async def main() -> None:
    try:
        with open("DBWork/DBPath.txt", "r") as dbp:
            dbpath = dbp.read()
        db = DBSqlite(dbpath)
    except Exception as excp:
        print('Can`t establish connection to database')
        print(excp)
        return

    while True:
        try:
            print(
                "\n\nМеню\n1) Вывод информации\n2) Ввести покупку\n3) Изменить покупку"
                "\n4) Удалить покупку\n5) Выход"
            )
            men = input("Выберите пункт меню: ")
            if men == '1':
                await show_purchases(db)
            elif men == '2':
                await insert_purchase(db)
            elif men == '3':
                await update_purchase(db)
            elif men == '4':
                await delete_purchase(db)
            elif men == '5':
                break
        except Exception as excp:
            print(type(excp))
            print(excp.args)


asyncio.run(main())
