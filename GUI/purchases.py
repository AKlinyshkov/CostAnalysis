import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QCoreApplication, QStringListModel
from PyQt5.QtWidgets import QApplication, QListView, QDialog, QTableWidgetItem
from PyQt5 import QtCore, QtWidgets, QtGui
from dbwork.dbsqlite import DBSqlite
from dbwork.dbmain import Purchase, DBWork
import datetime
import categories
from guiTemplate import AddItemDialog, ChangeItemDialog, ItemDialog

# import importlib.util

# spec = importlib.util.spec_from_file_location(
#     name="test_cat",  # note that ".test" is not a valid module name
#     location=".test/.test_UI_aux.py",
# )
# test_cat = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(test_cat)


class PurchaseModel(QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            purchase = self._data[index.row()]
            column_name = self._headers[index.column()]

            if column_name == "Date":
                return purchase.date
            elif column_name == "Product":
                return purchase.product
            elif column_name == "Description":
                return purchase.desc
            elif column_name == "Cost":
                return str(purchase.cost)
            elif column_name == "Sum":
                return str(purchase.sum_)
            elif column_name == "ID":
                return str(purchase.id_)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return str(self._headers[section])
        return QVariant()


class AddPurchaseDialog(AddItemDialog):
    def __init__(self, db: DBWork):

        window_title = "Add new purchases"
        window_size = (940, 670)
        table_size = (20, 20, 900, 330)
        table_headers = ['Дата', 'Товар', 'Описание', 'Цена', 'Сумма']
        column_width = [(0, 80), (1, 200), (2, 400)]
        hint_pos = (20, 400)

        super().__init__(window_title, window_size, table_size, table_headers, column_width)

        # Add listview and comboBox for hint
        self.addHint(db, hint_pos, window_size)

    def addHint(self, db: DBWork, hint_pos: tuple[int, int], window_size: tuple[int, int]):

        self.db = db

        # Заголовок
        self.labelHead = QtWidgets.QLabel(self)
        self.labelHead.setObjectName("labelHead")
        self.labelHead.setGeometry(QtCore.QRect(hint_pos[0], hint_pos[1], 280, 31))
        fontHead = QtGui.QFont()
        fontHead.setFamily(u"Verdana")
        fontHead.setPointSize(11)
        fontHead.setBold(True)
        fontHead.setWeight(75)
        self.labelHead.setFont(fontHead)
        self.labelHead.setText(QCoreApplication.translate("Dialog", "Товары определенной категории", None))

        # Пометка
        self.labelCat = QtWidgets.QLabel(self)
        self.labelCat.setObjectName("labelCat")
        self.labelCat.setGeometry(QtCore.QRect(hint_pos[0], hint_pos[1] + 35, 85, 21))
        fontCat = QtGui.QFont()
        fontCat.setPointSize(11)
        self.labelCat.setFont(fontCat)
        self.labelCat.setText(QCoreApplication.translate("Dialog", "Категория:", None))

        # Выпадающий список
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QtCore.QRect(hint_pos[0] + 90, hint_pos[1] + 35, 340, 24))

        # Вывод текста
        self.listView = QtWidgets.QListView(self)
        self.listView.setObjectName("listView")
        self.listView.setGeometry(QtCore.QRect(hint_pos[0], hint_pos[1] + 70, window_size[0] - 40, 130))
        fontList = QtGui.QFont()
        fontList.setPointSize(10)
        self.listView.setFont(fontList)
        self.listView.setAutoFillBackground(False)
        self.listView.setStyleSheet(u"background-color: rgb(240, 240, 240);\n")

        self.layout.addWidget(self.listView)
        self.layout.addWidget(self.comboBox)

        self.comboBox.activated.connect(self.changeCategory)
        categories = asyncio.run(self.db.get_list_categories())
        self.comboBox.addItems(categories)

        # Инициализация модели данных
        self.update_view_data(self.comboBox.currentText())

    def changeCategory(self, _):
        self.update_view_data(self.comboBox.currentText())

    def update_view_data(self, category):
        data = asyncio.run(self.db.select_product_by_category(category))
        model = QStringListModel()
        model.setStringList(data)
        self.listView.setModel(model)

    def add_row_to_table(self):
        date = str(datetime.date.today())

        # Вставляем новую строку в таблицу
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        # Устанавливаем данные в ячейки новой строки
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(date))

    def commitTableData(self):
        self.purchases = []
        for row in range(self.tableWidget.rowCount()):
            purchase = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                item = item if item is not None else self.tableWidget.item(row, col - 1)
                purchase.append(item.text())
            self.purchases.append(Purchase(date=purchase[0], product=purchase[1], desc=purchase[2], cost=float(purchase[3]), sum_=float(purchase[4])))
        self.accept()


class EditPurchaseDialog(ChangeItemDialog):
    def __init__(self, db: DBWork):
        window_title = "Edit purchases"
        window_size = (1070, 475)
        table_size = (20, 20, 1030, 350)
        table_headers = ['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum', 'Status']
        column_width = [(0, 10), (1, 80), (2, 200), (3, 400), (6, 80)]

        super().__init__(db, window_title, window_size, table_size, table_headers, column_width)

    def rowCount(self):
        return self.db.pur_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_purchases(page_num, self.row_per_page))
        self.tableWidget.setRowCount(len(data))

        for row, purchase in enumerate(data):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(purchase.id_)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(purchase.date))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(purchase.product))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(purchase.desc))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(purchase.cost)))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(str(purchase.sum_)))
            self.tableWidget.setItem(row, 6, QTableWidgetItem('Old'))

    def changeItem(self):
        row = self.tableWidget.currentRow()

        eitem = []
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(row, col)
            item = item if item is not None else self.tableWidget.item(row, col-1)
            eitem.append(item.text())

        self.changedItems.append(Purchase(id_=eitem[0], date=eitem[1], product=eitem[2], desc=eitem[3], cost=float(eitem[4]), sum_=float(eitem[5])))
        self.tableWidget.setItem(row, 6, QTableWidgetItem('Edited'))


class DeletePurchaseDialog(ChangeItemDialog):
    def __init__(self, db: DBWork):
        window_title = "Delete purchases"
        window_size = (1070, 475)
        table_size = (20, 20, 1030, 350)
        table_headers = ['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum', 'Status']
        column_width = [(0, 10), (1, 80), (2, 200), (3, 400), (6, 80)]
        
        super().__init__(db, window_title, window_size, table_size, table_headers, column_width)

    def rowCount(self):
        return self.db.pur_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_purchases(page_num, self.row_per_page))
        self.tableWidget.setRowCount(len(data))

        for row, purchase in enumerate(data):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(purchase.id_)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(purchase.date))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(purchase.product))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(purchase.desc))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(purchase.cost)))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(str(purchase.sum_)))
            self.tableWidget.setItem(row, 6, QTableWidgetItem('Old'))

    def changeItem(self):
        row = self.tableWidget.currentRow()

        self.changedItems.append(self.tableWidget.item(row, 0).text())

        self.tableWidget.setItem(row, 6, QTableWidgetItem('Deleted'))


class PurchaseDialog(ItemDialog):
    def __init__(self, db: DBWork):
        window_size = (980, 500)
        window_title = "Purchases"
        table_size = (20, 20, 940, 330)
        table_headers = ['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum']
        column_width = [(0, 10), (1, 80), (2, 200), (3, 400)]

        super().__init__(db, window_size, window_title, table_size, table_headers, column_width)

        # Кнопка для вызова окна работы с категориями
        _translate = QtCore.QCoreApplication.translate
        self.go2Cat = QtWidgets.QPushButton(self)
        self.go2Cat.setGeometry(QtCore.QRect(20, 465, 75, 24))
        self.go2Cat.setObjectName("go2Cat")
        self.go2Cat.setText(_translate("Dialog", "Categories"))
        self.go2Cat.clicked.connect(self.goToCat)

    def rowCount(self):
        return self.db.pur_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_purchases(page_num, self.row_per_page))
        self.model = PurchaseModel(data, self.headers)
        self.tableView.setModel(self.model)
        for colw in self.column_width:
            self.tableView.setColumnWidth(colw[0], colw[1])

    def addItem(self):
        # Вызов диалога внесения данных
        add_purchase_dialog = AddPurchaseDialog(self.db)
        result = add_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            purchases = add_purchase_dialog.purchases

            # Корректировака выпадающего списка
            _translate = QtCore.QCoreApplication.translate
            count = len(purchases)
            newItemCount = (self.db.pur_count + count - 1) // self.row_per_page + 1
            for pn in range(self.page_count, newItemCount):
                self.comboBox.addItem("")
                self.comboBox.setItemText(pn, _translate("Dialog", f"{pn + 1}"))

            # Внесение данных в БД
            for pur in purchases:
                asyncio.run(self.db.insert_into_purchases(pur))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def editItem(self):
        # Вызов диалога внесения данных
        edit_purchase_dialog = EditPurchaseDialog(self.db)
        result = edit_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            edited_purchases = edit_purchase_dialog.changedItems

            # Внесение данных в БД
            for pur in edited_purchases:
                asyncio.run(self.db.update_purchases(pur))

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def deleteItem(self):
        # Вызов диалога внесения данных
        delete_purchase_dialog = DeletePurchaseDialog(self.db)
        result = delete_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            deleted_purchases = delete_purchase_dialog.changedItems

            # Корректировака выпадающего списка
            count = len(deleted_purchases)
            newItemCount = (self.db.pur_count - count - 1) // self.row_per_page + 1
            for pn in range(self.page_count - newItemCount):
                self.comboBox.removeItem(self.comboBox.count() - 1)

            # Внесение данных в БД
            for pur in deleted_purchases:
                asyncio.run(self.db.delete_from_purchases(int(pur)))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def goToCat(self):
        # Вызов диалога внесения данных
        category_dialog = categories.CategoryDialog(self.db)
        category_dialog.exec_()


if __name__ == "__main__":
    try:
        with open("DBWork/DBPath.txt", "r") as dbp:
            dbpath = dbp.read()
        db = DBSqlite(dbpath)
    except Exception:  # as excp:
        pass

    app = QApplication(sys.argv)
    dialog = PurchaseDialog(db)
    dialog.show()
    sys.exit(app.exec_())
