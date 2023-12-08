import sys
import os
from PyQt5.QtWidgets import QVBoxLayout, QDialog
from PyQt5 import QtCore, QtWidgets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dbwork.dbmain import DBWork


class AddItemDialog(QDialog):
    def __init__(self, window_title, window_size, table_size, table_headers, column_width):
        super().__init__()
        self.setWindowTitle(window_title)
        self.resize(window_size[0], window_size[1])

        # Создаем QTableWidget
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(table_size[0], table_size[1], table_size[2], table_size[3])
        self.tableWidget.setColumnCount(len(table_headers))  # Устанавливаем количество столбцов
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        for colw in column_width:
            self.tableWidget.setColumnWidth(colw[0], colw[1])

        table_bottom = table_size[1] + table_size[3]
        window_center = window_size[0] // 2

        # Создаем кнопку для удаления последней строки
        self.delRow = QtWidgets.QPushButton('Удалить стоку', self)
        self.delRow.setGeometry(window_center - 121, table_bottom + 10, 120, 24)
        self.delRow.clicked.connect(self.del_row_from_table)

        # Создаем кнопку для добавления новой строки
        self.newRow = QtWidgets.QPushButton('Новая стока', self)
        self.newRow.setGeometry(window_center + 1, table_bottom + 10, 120, 24)
        self.newRow.clicked.connect(self.add_row_to_table)

        # Создаем кнопку для получения данных из таблицы
        self.commitData = QtWidgets.QPushButton('Добавить', self)
        self.commitData.setGeometry(window_size[0] - 145, window_size[1] - 35, 125, 24)
        self.commitData.clicked.connect(self.commitTableData)

        # Создаем кнопку для отмены
        self.cancelData = QtWidgets.QPushButton('Отмена', self)
        self.cancelData.setGeometry(window_size[0] - 272, window_size[1] - 35, 125, 24)
        self.cancelData.clicked.connect(self.close)

        # Создаем макет и добавляем таблицу и кнопку
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.newRow)
        self.layout.addWidget(self.delRow)
        self.layout.addWidget(self.commitData)
        self.layout.addWidget(self.cancelData)

    def del_row_from_table(self):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.removeRow(row_position - 1)

    def add_row_to_table(self):
        pass
    
    def commitTableData(self):
        pass


class ChangeItemDialog(QDialog):
    def __init__(self, db: DBWork, window_title, window_size, table_size, table_headers, column_width):
        super().__init__()

        # Инициализация параметров
        self.row_per_page = 10
        self.db = db
        self.page_count = (self.rowCount() - 1) // self.row_per_page + 1

        self.changedItems = []

        self.setWindowTitle(window_title)
        self.resize(window_size[0], window_size[1])

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(table_size[0], table_size[1], table_size[2], table_size[3]))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        for colw in column_width:
            self.tableWidget.setColumnWidth(colw[0], colw[1])

        window_center = window_size[0] // 2
        table_bottom = table_size[1] + table_size[3]

        self.Past = QtWidgets.QPushButton(self)
        self.Past.setGeometry(QtCore.QRect(window_center - 78, table_bottom + 10, 50, 23))
        self.Past.setObjectName("Past")

        self.Next = QtWidgets.QPushButton(self)
        self.Next.setGeometry(QtCore.QRect(window_center - 27, table_bottom + 10, 50, 23))
        self.Next.setObjectName("Next")

        self.Change = QtWidgets.QPushButton(self)
        self.Change.setGeometry(QtCore.QRect(window_center + 32, table_bottom + 10, 190, 24))
        self.Change.setObjectName("Change")

        self.Commit = QtWidgets.QPushButton(self)
        self.Commit.setGeometry(QtCore.QRect(window_size[0] - 170, window_size[1] - 35, 150, 24))
        self.Commit.setObjectName("Commit")

        self.Cancel = QtWidgets.QPushButton(self)
        self.Cancel.setGeometry(QtCore.QRect(window_size[0] - 322, window_size[1] - 35, 150, 24))
        self.Cancel.setObjectName("Cancel")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(window_center - 122, table_bottom + 10, 40, 22))
        self.comboBox.setObjectName("comboBox")

        self.retranslateUi()

        # Инициализация виджетов
        self.Past.clicked.connect(self.buttonPast)
        self.Next.clicked.connect(self.buttonNext)
        self.Change.clicked.connect(self.changeItem)
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
        self.Change.setText(_translate("Dialog", "Выбрать"))
        self.Commit.setText(_translate("Dialog", "Подтвердить"))
        self.Cancel.setText(_translate("Dialog", "Отмена"))

    def update_table_data(self, page_num):
        pass

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

    def changeItem(self):
        pass

    def rowCount(self):
        pass


class ItemDialog(QDialog):
    def __init__(self, db: DBWork, window_size, window_title, table_size, table_headers, column_width):
        super().__init__()

        # Инициализация параметров
        self.row_per_page = 10
        self.db = db
        self.page_count = (self.rowCount() - 1) // self.row_per_page + 1
        self.column_width = column_width

        # Инициализация интерфейса
        self.setObjectName("Dialog")
        self.resize(window_size[0], window_size[1])

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setGeometry(QtCore.QRect(table_size[0], table_size[1], table_size[2], table_size[3]))
        self.tableView.setObjectName("tableView")

        window_center = window_size[0] // 2
        table_bottom = table_size[1] + table_size[3]

        self.Past = QtWidgets.QPushButton(self)
        self.Past.setGeometry(QtCore.QRect(window_center - 29, table_bottom + 10, 50, 23))
        self.Past.setObjectName("Past")

        self.Next = QtWidgets.QPushButton(self)
        self.Next.setGeometry(QtCore.QRect(window_center + 23, table_bottom + 10, 50, 23))
        self.Next.setObjectName("Next")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(window_center - 73, table_bottom + 10, 40, 22))
        self.comboBox.setObjectName("comboBox")

        button_width = (window_size[0] - 80) // 3
        button_start = window_center - (window_size[0] - 40) // 2

        self.AddItem = QtWidgets.QPushButton(self)
        self.AddItem.setGeometry(QtCore.QRect(button_start, table_bottom + 60, button_width, 23))
        self.AddItem.setObjectName("Add Item")

        self.EditItem = QtWidgets.QPushButton(self)
        self.EditItem.setGeometry(QtCore.QRect(button_start + button_width + 20, table_bottom + 60, button_width, 23))
        self.EditItem.setObjectName("Edit Item")

        self.DeleteItem = QtWidgets.QPushButton(self)
        self.DeleteItem.setGeometry(QtCore.QRect(button_start + button_width * 2 + 40, table_bottom + 60, button_width, 23))
        self.DeleteItem.setObjectName("Delete Item")

        self.Exit = QtWidgets.QPushButton(self)
        self.Exit.setGeometry(QtCore.QRect(window_size[0] - 130, window_size[1] - 35, 110, 23))
        self.Exit.setObjectName("Exit")

        # Добавление названий элементам
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", window_title))
        self.Past.setText(_translate("Dialog", "^"))
        self.Next.setText(_translate("Dialog", "v"))
        self.AddItem.setText(_translate("Dialog", "Add Item"))
        self.EditItem.setText(_translate("Dialog", "Edit Item"))
        self.DeleteItem.setText(_translate("Dialog", "Delete Item"))
        self.Exit.setText(_translate("Dialog", "Exit"))
        QtCore.QMetaObject.connectSlotsByName(self)

        # Инициализация виджетов
        self.Past.clicked.connect(self.buttonPast)
        self.Next.clicked.connect(self.buttonNext)
        self.AddItem.clicked.connect(self.addItem)
        self.EditItem.clicked.connect(self.editItem)
        self.DeleteItem.clicked.connect(self.deleteItem)
        self.Exit.clicked.connect(self.close)
        self.comboBox.activated.connect(self.changePageNum)
        _translate = QtCore.QCoreApplication.translate
        for pn in range(self.page_count):
            self.comboBox.addItem("")
            self.comboBox.setItemText(pn, _translate("Dialog", f"{pn+1}"))

        # Инициализация модели данных
        self.headers = table_headers
        self.comboBox.setCurrentIndex(self.page_count - 1)
        self.comboBox.currentIndexChanged.emit(self.page_count - 1)
        self.update_table_data(self.comboBox.currentIndex())

    def update_table_data(self, page_num):
        pass

    def addItem(self):
        pass

    def editItem(self):
        pass

    def deleteItem(self):
        pass

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

    def rowCount(self):
        pass
