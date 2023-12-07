import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QDialog, QTableWidgetItem
from PyQt5 import QtCore, QtWidgets
from dbwork.dbsqlite import DBSqlite
from dbwork.dbmain import Purchase, DBWork
import datetime
import categories

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


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(980, 500)

        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(20, 20, 940, 330))
        self.tableView.setObjectName("tableView")

        self.Past = QtWidgets.QPushButton(Dialog)
        self.Past.setGeometry(QtCore.QRect(460, 360, 51, 23))
        self.Past.setObjectName("Past")

        self.Next = QtWidgets.QPushButton(Dialog)
        self.Next.setGeometry(QtCore.QRect(510, 360, 51, 23))
        self.Next.setObjectName("Next")

        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(415, 360, 41, 22))
        self.comboBox.setObjectName("comboBox")

        self.AddItem = QtWidgets.QPushButton(Dialog)
        self.AddItem.setGeometry(QtCore.QRect(20, 410, 300, 23))
        self.AddItem.setObjectName("Add Item")

        self.EditItem = QtWidgets.QPushButton(Dialog)
        self.EditItem.setGeometry(QtCore.QRect(340, 410, 300, 23))
        self.EditItem.setObjectName("Edit Item")

        self.DeleteItem = QtWidgets.QPushButton(Dialog)
        self.DeleteItem.setGeometry(QtCore.QRect(660, 410, 300, 23))
        self.DeleteItem.setObjectName("Delete Item")

        self.Exit = QtWidgets.QPushButton(Dialog)
        self.Exit.setGeometry(QtCore.QRect(854, 470, 111, 23))
        self.Exit.setObjectName("Exit")

        self.go2Cat = QtWidgets.QPushButton(Dialog)
        self.go2Cat.setGeometry(QtCore.QRect(20, 465, 75, 24))
        self.go2Cat.setObjectName("go2Cat")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Purchases"))
        self.Past.setText(_translate("Dialog", "^"))
        self.Next.setText(_translate("Dialog", "v"))
        self.AddItem.setText(_translate("Dialog", "Add Item"))
        self.EditItem.setText(_translate("Dialog", "Edit Item"))
        self.DeleteItem.setText(_translate("Dialog", "Delete Item"))
        self.Exit.setText(_translate("Dialog", "Exit"))
        self.go2Cat.setText(_translate("Dialog", "Categories"))


class AddPurchaseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add new purchases")
        self.resize(940, 445)
        # self.setGeometry(400, 400, 940, 445)

        # Создаем QTableWidget
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(20, 20, 900, 330)
        self.tableWidget.setColumnCount(5)  # Устанавливаем количество столбцов
        self.tableWidget.setHorizontalHeaderLabels(['Дата', 'Товар', 'Описание', 'Цена', 'Сумма'])
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 400)

        # Создаем кнопку для удаления последней строки
        self.delRow = QtWidgets.QPushButton('Удалить стоку', self)
        self.delRow.setGeometry(359, 360, 120, 24)
        self.delRow.clicked.connect(self.del_row_from_table)

        # Создаем кнопку для добавления новой строки
        self.newRow = QtWidgets.QPushButton('Новая стока', self)
        self.newRow.setGeometry(481, 360, 120, 24)
        self.newRow.clicked.connect(self.add_row_to_table)

        # Создаем кнопку для получения данных из таблицы
        self.commitData = QtWidgets.QPushButton('Добавить покупки', self)
        self.commitData.setGeometry(795, 410, 125, 24)
        self.commitData.clicked.connect(self.commitTableData)

        # Создаем кнопку для отмены
        self.cancelData = QtWidgets.QPushButton('Отмена', self)
        self.cancelData.setGeometry(668, 410, 125, 24)
        self.cancelData.clicked.connect(self.close)

        # Создаем макет и добавляем таблицу и кнопку
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addWidget(self.newRow)
        layout.addWidget(self.delRow)
        layout.addWidget(self.commitData)
        layout.addWidget(self.cancelData)

    def del_row_from_table(self):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.removeRow(row_position - 1)

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
                item = item if item is not None else self.tableWidget.item(row, col-1)
                purchase.append(item.text())
            self.purchases.append(Purchase(date=purchase[0], product=purchase[1], desc=purchase[2], cost=float(purchase[3]), sum_=float(purchase[4])))
        self.accept()


class EditPurchaseDialog(QDialog):
    def __init__(self, db: DBWork):
        super().__init__()

        # Инициализация параметров
        self.row_per_page = 10
        self.db = db
        self.page_count = (self.db.pur_count - 1) // self.row_per_page + 1

        self.editedItems = []

        self.setWindowTitle("Edit purchases")
        self.resize(1070, 475)

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(20, 20, 1030, 350))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)  # Set the number of columns
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum', 'Status'])
        self.tableWidget.setColumnWidth(0, 10)
        self.tableWidget.setColumnWidth(1, 80)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 400)
        self.tableWidget.setColumnWidth(6, 80)

        self.Past = QtWidgets.QPushButton(self)
        self.Past.setGeometry(QtCore.QRect(460, 380, 51, 23))
        self.Past.setObjectName("Past")

        self.Next = QtWidgets.QPushButton(self)
        self.Next.setGeometry(QtCore.QRect(510, 380, 51, 23))
        self.Next.setObjectName("Next")

        self.Edit = QtWidgets.QPushButton(self)
        self.Edit.setGeometry(QtCore.QRect(570, 380, 191, 24))
        self.Edit.setObjectName("Edit")

        self.Commit = QtWidgets.QPushButton(self)
        self.Commit.setGeometry(QtCore.QRect(900, 440, 150, 24))
        self.Commit.setObjectName("Commit")

        self.Cancel = QtWidgets.QPushButton(self)
        self.Cancel.setGeometry(QtCore.QRect(748, 440, 150, 24))
        self.Cancel.setObjectName("Cancel")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(415, 380, 41, 22))
        self.comboBox.setObjectName("comboBox")

        self.retranslateUi()

        # Инициализация виджетов
        self.Past.clicked.connect(self.buttonPast)
        self.Next.clicked.connect(self.buttonNext)
        self.Edit.clicked.connect(self.editItem)
        self.Cancel.clicked.connect(self.close)
        self.Commit.clicked.connect(self.accept)
        self.comboBox.activated.connect(self.changePageNum)
        _translate = QtCore.QCoreApplication.translate
        for pn in range(self.page_count):
            self.comboBox.addItem("")
            self.comboBox.setItemText(pn, _translate("Dialog", f"{pn+1}"))

        # Инициализация модели данных
        self.comboBox.setCurrentIndex(self.page_count - 1)
        self.comboBox.currentIndexChanged.emit(self.page_count - 1)
        self.update_table_data(self.comboBox.currentIndex())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Past.setText(_translate("Dialog", "^"))
        self.Next.setText(_translate("Dialog", "v"))
        self.Edit.setText(_translate("Dialog", "Изменить"))
        self.Commit.setText(_translate("Dialog", "Подтвердить"))
        self.Cancel.setText(_translate("Dialog", "Отмена"))

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

    def buttonPast(self):
        if self.comboBox.currentIndex() - 1 >= 0:
            self.comboBox.setCurrentIndex(self.comboBox.currentIndex() - 1)
            self.comboBox.currentIndexChanged.emit(self.comboBox.currentIndex() - 1)
            self.update_table_data(self.comboBox.currentIndex())

    def buttonNext(self):
        if self.comboBox.currentIndex() + 1 < self.page_count:
            self.comboBox.setCurrentIndex(self.comboBox.currentIndex() + 1)
            self.comboBox.currentIndexChanged.emit(self.comboBox.currentIndex() + 1)
            self.update_table_data(self.comboBox.currentIndex())

    def changePageNum(self, index):
        self.update_table_data(index)

    def editItem(self):
        row = self.tableWidget.currentRow()

        eitem = []
        for col in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(row, col)
            item = item if item is not None else self.tableWidget.item(row, col-1)
            eitem.append(item.text())

        self.editedItems.append(Purchase(id_=eitem[0], date=eitem[1], product=eitem[2], desc=eitem[3], cost=float(eitem[4]), sum_=float(eitem[5])))
        self.tableWidget.setItem(row, 6, QTableWidgetItem('Edited'))


class DeletePurchaseDialog(QDialog):
    def __init__(self, db: DBWork):
        super().__init__()

        # Инициализация параметров
        self.row_per_page = 10
        self.db = db
        self.page_count = (self.db.pur_count - 1) // self.row_per_page + 1

        self.deletedItems = []

        self.setWindowTitle("Delete purchases")
        self.resize(1070, 475)

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(20, 20, 1030, 350))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)  # Set the number of columns
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum', 'Status'])
        self.tableWidget.setColumnWidth(0, 10)
        self.tableWidget.setColumnWidth(1, 80)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 400)
        self.tableWidget.setColumnWidth(6, 80)

        self.Past = QtWidgets.QPushButton(self)
        self.Past.setGeometry(QtCore.QRect(460, 380, 51, 23))
        self.Past.setObjectName("Past")

        self.Next = QtWidgets.QPushButton(self)
        self.Next.setGeometry(QtCore.QRect(510, 380, 51, 23))
        self.Next.setObjectName("Next")

        self.Delete = QtWidgets.QPushButton(self)
        self.Delete.setGeometry(QtCore.QRect(570, 380, 191, 24))
        self.Delete.setObjectName("Delete")

        self.Commit = QtWidgets.QPushButton(self)
        self.Commit.setGeometry(QtCore.QRect(900, 440, 150, 24))
        self.Commit.setObjectName("Commit")

        self.Cancel = QtWidgets.QPushButton(self)
        self.Cancel.setGeometry(QtCore.QRect(748, 440, 150, 24))
        self.Cancel.setObjectName("Cancel")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(415, 380, 41, 22))
        self.comboBox.setObjectName("comboBox")

        self.retranslateUi()

        # Инициализация виджетов
        self.Past.clicked.connect(self.buttonPast)
        self.Next.clicked.connect(self.buttonNext)
        self.Delete.clicked.connect(self.deleteItem)
        self.Cancel.clicked.connect(self.close)
        self.Commit.clicked.connect(self.accept)
        self.comboBox.activated.connect(self.changePageNum)
        _translate = QtCore.QCoreApplication.translate
        for pn in range(self.page_count):
            self.comboBox.addItem("")
            self.comboBox.setItemText(pn, _translate("Dialog", f"{pn+1}"))

        # Инициализация модели данных
        self.comboBox.setCurrentIndex(self.page_count - 1)
        self.comboBox.currentIndexChanged.emit(self.page_count - 1)
        self.update_table_data(self.comboBox.currentIndex())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.Past.setText(_translate("Dialog", "^"))
        self.Next.setText(_translate("Dialog", "v"))
        self.Delete.setText(_translate("Dialog", "Удалить"))
        self.Commit.setText(_translate("Dialog", "Подтвердить"))
        self.Cancel.setText(_translate("Dialog", "Отмена"))

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

    def buttonPast(self):
        if self.comboBox.currentIndex() - 1 >= 0:
            self.comboBox.setCurrentIndex(self.comboBox.currentIndex() - 1)
            self.comboBox.currentIndexChanged.emit(self.comboBox.currentIndex() - 1)
            self.update_table_data(self.comboBox.currentIndex())

    def buttonNext(self):
        if self.comboBox.currentIndex() + 1 < self.page_count:
            self.comboBox.setCurrentIndex(self.comboBox.currentIndex() + 1)
            self.comboBox.currentIndexChanged.emit(self.comboBox.currentIndex() + 1)
            self.update_table_data(self.comboBox.currentIndex())

    def changePageNum(self, index):
        self.update_table_data(index)

    def deleteItem(self):
        row = self.tableWidget.currentRow()

        self.deletedItems.append(self.tableWidget.item(row, 0).text())

        self.tableWidget.setItem(row, 6, QTableWidgetItem('Deleted'))


class PurchaseDialog(QDialog):
    def __init__(self, db: DBWork):
        super().__init__()

        # Инициализация параметров
        self.row_per_page = 10
        self.db = db
        self.page_count = (self.db.pur_count - 1) // self.row_per_page + 1

        # Инициализация интерфейса
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Инициализация виджетов
        self.ui.Past.clicked.connect(self.buttonPast)
        self.ui.Next.clicked.connect(self.buttonNext)
        self.ui.AddItem.clicked.connect(self.addPurcahses)
        self.ui.EditItem.clicked.connect(self.editPurcahses)
        self.ui.DeleteItem.clicked.connect(self.deletePurcahses)
        self.ui.Exit.clicked.connect(self.close)
        self.ui.go2Cat.clicked.connect(self.goToCat)
        self.ui.comboBox.activated.connect(self.changePageNum)
        _translate = QtCore.QCoreApplication.translate
        for pn in range(self.page_count):
            self.ui.comboBox.addItem("")
            self.ui.comboBox.setItemText(pn, _translate("Dialog", f"{pn+1}"))

        # Инициализация модели данных
        self.headers = ['ID', 'Date', 'Product', 'Description', 'Cost', 'Sum']
        self.ui.comboBox.setCurrentIndex(self.page_count - 1)
        self.ui.comboBox.currentIndexChanged.emit(self.page_count - 1)
        self.update_table_data(self.ui.comboBox.currentIndex())

    def update_table_data(self, page_num):
        data = asyncio.run(self.db.select_page_purchases(page_num, self.row_per_page))
        self.model = PurchaseModel(data, self.headers)
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setColumnWidth(0, 10)
        self.ui.tableView.setColumnWidth(1, 80)
        self.ui.tableView.setColumnWidth(2, 200)
        self.ui.tableView.setColumnWidth(3, 400)

    def addPurcahses(self):
        # Вызов диалога внесения данных
        add_purchase_dialog = AddPurchaseDialog()
        result = add_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            purchases = add_purchase_dialog.purchases

            # Корректировака выпадающего списка
            _translate = QtCore.QCoreApplication.translate
            count = len(purchases)
            newItemCount = (self.db.pur_count + count - 1) // self.row_per_page + 1
            for pn in range(self.page_count, newItemCount):
                self.ui.comboBox.addItem("")
                self.ui.comboBox.setItemText(pn, _translate("Dialog", f"{pn + 1}"))

            # Внесение данных в БД
            for pur in purchases:
                asyncio.run(self.db.insert_into_purchases(pur))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.ui.comboBox.setCurrentIndex(self.page_count - 1)
            self.ui.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def editPurcahses(self):
        # Вызов диалога внесения данных
        edit_purchase_dialog = EditPurchaseDialog(self.db)
        result = edit_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            edited_purchases = edit_purchase_dialog.editedItems

            # Внесение данных в БД
            for pur in edited_purchases:
                asyncio.run(self.db.update_purchases(pur))

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.ui.comboBox.setCurrentIndex(self.page_count - 1)
            self.ui.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def deletePurcahses(self):
        # Вызов диалога внесения данных
        delete_purchase_dialog = DeletePurchaseDialog(self.db)
        result = delete_purchase_dialog.exec_()

        if result == QDialog.Accepted:
            # Получение данных
            deleted_purchases = delete_purchase_dialog.deletedItems

            # Корректировака выпадающего списка
            count = len(deleted_purchases)
            newItemCount = (self.db.pur_count - count - 1) // self.row_per_page + 1
            for pn in range(self.page_count - newItemCount):
                self.ui.comboBox.removeItem(self.ui.comboBox.count() - 1)

            # Внесение данных в БД
            for pur in deleted_purchases:
                asyncio.run(self.db.delete_from_purchases(int(pur)))

            # Корректировка параметров
            self.page_count = newItemCount

            # Обновление страницы
            self.update_table_data(self.page_count - 1)
            self.ui.comboBox.setCurrentIndex(self.page_count - 1)
            self.ui.comboBox.currentIndexChanged.emit(self.page_count - 1)

    def buttonPast(self):
        if self.ui.comboBox.currentIndex() - 1 >= 0:
            self.ui.comboBox.setCurrentIndex(self.ui.comboBox.currentIndex() - 1)
            self.ui.comboBox.currentIndexChanged.emit(self.ui.comboBox.currentIndex() - 1)
            self.update_table_data(self.ui.comboBox.currentIndex())

    def buttonNext(self):
        if self.ui.comboBox.currentIndex() + 1 < self.page_count:
            self.ui.comboBox.setCurrentIndex(self.ui.comboBox.currentIndex() + 1)
            self.ui.comboBox.currentIndexChanged.emit(self.ui.comboBox.currentIndex() + 1)
            self.update_table_data(self.ui.comboBox.currentIndex())

    def changePageNum(self, index):
        self.update_table_data(index)

    def goToCat(self):
        # Вызов диалога внесения данных
        category_dialog = categories.CategoryDialog(self.db)
        result = category_dialog.exec_()


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


# Поправил PurchaseDialog и EditDialog 
# Заменить Dbsqlite на dbwork