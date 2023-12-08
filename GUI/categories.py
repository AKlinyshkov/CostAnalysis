import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QDialog, QTableWidgetItem
from PyQt5 import QtCore, QtWidgets
from dbwork.dbsqlite import DBSqlite
from dbwork.dbmain import Category, DBWork
from guiTemplate import ChangeItemDialog, AddItemDialog, ItemDialog


class CategoryModel(QAbstractTableModel):
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
            category = self._data[index.row()]
            column_name = self._headers[index.column()]

            if column_name == "Category":
                return category.category
            elif column_name == "Product":
                return category.product
            elif column_name == "Hint":
                return category.hint
            elif column_name == "ID":
                return category.id_

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return str(self._headers[section])
        return QVariant()


class AddCategoryDialog(AddItemDialog):
    def __init__(self):
        window_title = "Add new categories"
        window_size = (940, 445)
        table_size = (20, 20, 900, 330)
        table_headers = ['Категория', 'Товар', 'Описание']
        column_width = [(0, 200), (1, 200), (2, 480)]

        super().__init__(window_title, window_size, table_size, table_headers, column_width)

    def add_row_to_table(self):
        # Вставляем новую строку в таблицу
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        # Устанавливаем данные в ячейки новой строки
        if row_position != 0:
            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(self.tableWidget.item(row_position-1, 0)))

    def commitTableData(self):
        self.categories = []
        for row in range(self.tableWidget.rowCount()):
            category = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                item = item if item is not None else self.tableWidget.item(row, col-1)
                category.append(item.text())
            self.categories.append(Category(category=category[0], product=category[1], hint=category[2]))
        self.accept()


class EditCategoryDialog(ChangeItemDialog):
    def __init__(self, db: DBWork):
        window_title = "Edit categories"
        window_size = (1070, 475)
        table_size = (20, 20, 1030, 350)
        table_headers = ['ID', 'Category', 'Product', 'Hint', 'Status']
        column_width = [(0, 10), (1, 200), (2, 200), (3, 480), (4, 80)]

        super().__init__(db, window_title, window_size, table_size, table_headers, column_width)

    def rowCount(self):
        db_cat_count = len(asyncio.run(self.db.select_all_categories()))
        return db_cat_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_categories(page_num, self.row_per_page))
        self.tableWidget.setRowCount(len(data))

        for row, category in enumerate(data):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(category.id_)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(category.category))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(category.product))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(category.hint))
            self.tableWidget.setItem(row, 4, QTableWidgetItem('Old'))

    def changeItem(self):
        row = self.tableWidget.currentRow()

        eitem = []
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(row, col)
            item = item if item is not None else self.tableWidget.item(row, col - 1)
            eitem.append(item.text())

        self.changedItems.append(Category(id_=int(eitem[0]), category=eitem[1], product=eitem[2], hint=eitem[3]))
        self.tableWidget.setItem(row, 4, QTableWidgetItem('Edited'))


class DeleteCategoryDialog(ChangeItemDialog):
    def __init__(self, db: DBWork):
        window_title = "Delete categories"
        window_size = (1070, 475)
        table_size = (20, 20, 1030, 350)
        table_headers = ['ID', 'Category', 'Product', 'Hint', 'Status']
        column_width = [(0, 10), (1, 200), (2, 200), (3, 480), (4, 80)]

        super().__init__(db, window_title, window_size, table_size, table_headers, column_width)

    def rowCount(self):
        db_cat_count = len(asyncio.run(self.db.select_all_categories()))
        return db_cat_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_categories(page_num, self.row_per_page))
        self.tableWidget.setRowCount(len(data))

        for row, category in enumerate(data):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(category.id_)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(category.category))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(category.product))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(category.hint))
            self.tableWidget.setItem(row, 4, QTableWidgetItem('Old'))

    def changeItem(self):
        row = self.tableWidget.currentRow()

        self.changedItems.append(self.tableWidget.item(row, 0).text())

        self.tableWidget.setItem(row, 4, QTableWidgetItem('Deleted'))


class CategoryDialog(ItemDialog):
    def __init__(self, db: DBWork):
        window_size = (980, 500)
        window_title = "Categories"
        table_size = (20, 20, 940, 330)
        table_headers = ['ID', 'Category', 'Product', 'Hint']
        column_width = [(0, 10), (1, 200), (2, 200), (3, 480)]
        
        super().__init__(db, window_size, window_title, table_size, table_headers, column_width)

    def rowCount(self):
        db_cat_count = len(asyncio.run(self.db.select_all_categories()))
        return db_cat_count

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_categories(page_num, self.row_per_page))
        self.model = CategoryModel(data, self.headers)
        self.tableView.setModel(self.model)
        for colw in self.column_width:
            self.tableView.setColumnWidth(colw[0], colw[1])

    def addItem(self):
        # Вызов диалога внесения данных
        add_category_dialog = AddCategoryDialog()
        result = add_category_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            categories = add_category_dialog.categories

            # Корректировака выпадающего списка
            _translate = QtCore.QCoreApplication.translate
            count = len(categories)
            db_cat_count = len(asyncio.run(self.db.select_all_categories()))
            newItemCount = (db_cat_count + count - 1) // self.row_per_page + 1
            for pn in range(self.page_count, newItemCount):
                self.comboBox.addItem("")
                self.comboBox.setItemText(pn, _translate("Dialog", f"{pn + 1}"))

            # Внесение данных в БД
            for cat in categories:
                asyncio.run(self.db.insert_into_categories(cat))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def editItem(self):
        # Вызов диалога внесения данных
        edit_category_dialog = EditCategoryDialog(self.db)
        result = edit_category_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            edited_categories = edit_category_dialog.changedItems

            # Внесение данных в БД
            for cat in edited_categories:
                asyncio.run(self.db.update_categories(cat))

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def deleteItem(self):
        # Вызов диалога внесения данных
        delete_category_dialog = DeleteCategoryDialog(self.db)
        result = delete_category_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            deleted_categories = delete_category_dialog.changedItems

            # Корректировака выпадающего списка
            count = len(deleted_categories)
            db_cat_count = len(asyncio.run(self.db.select_all_categories()))
            newItemCount = (db_cat_count - count - 1) // self.row_per_page + 1
            for pn in range(self.page_count - newItemCount):
                self.comboBox.removeItem(self.comboBox.count() - 1)

            # Внесение данных в БД
            for cat in deleted_categories:
                asyncio.run(self.db.delete_from_categories(int(cat)))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.comboBox.setCurrentIndex(self.page_count - 1)
            self.comboBox.currentIndexChanged.emit(self.page_count - 1)
