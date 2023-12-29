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
import pyqtgraph as pg
import numpy as np
from dateutil.relativedelta import relativedelta


class DayData():
    def __init__(self, dialog, period):
        start = period[0]
        finish = period[1]

        self.data = asyncio.run(dialog.db.select_sum_by_day((str(start), str(finish))))

        # Feeling zero days
        date_array = []
        current_date = start
        while current_date <= finish:
            date_array.append(str(current_date))
            current_date += datetime.timedelta(days=1)

        if date_array[len(date_array) - 1] != self.data[len(self.data) - 1][0]:
            self.data.append((date_array[len(date_array) - 1], 0))

        for i in range(len(date_array)):
            if date_array[i] != self.data[i][0]:
                self.data.insert(i, (date_array[i], 0))

        # Common parameters    
        self.ticks_value = 19
        self.XRange = [0, len(self.data) - 1]
        self.Label = 'Day Sum'

        # Parameter specific for day items
        dates = [datetime.date.fromisoformat(self.data[i][0]) for i in range(len(self.data))]
        self.ticks = [dates[i].strftime("%d.%m.%y") for i in range(len(dates))]
        ...

    def __getitem__(self, index):
        return self.data[index]

    def getTicks(self, num_ticks):
        ticks = [(i, self.ticks[i]) for i in range(0, len(self.data), num_ticks)]
        return ticks

    def length(self):
        return len(self.data)


class WeekData():
    def __init__(self, dialog, period):
        start = period[0]
        finish = period[1]

        self.data = asyncio.run(dialog.db.select_sum_by_week((str(start), str(finish))))

        # Feeling zero weeks
        date_array = []
        current_date = start

        while current_date <= finish:
            week_date = f"{current_date.isocalendar()[0]}-{current_date.isocalendar()[1]}"
            date_array.append(week_date)
            current_date += datetime.timedelta(days=7)

        if date_array[len(date_array) - 1] != self.data[len(self.data)-1][0]:
            self.data.append((date_array[len(date_array)-1], 0))

        for i in range(len(date_array)):
            if date_array[i] != self.data[i][0]:
                self.data.insert(i,(date_array[i], 0))

        for i in range(len(self.data)):
            self.data[i] = (self.date_by_week(self.data[i][0]), self.data[i][1])

        # Common parameters
        self.ticks_value = 13
        self.XRange = [-1, len(self.data)]
        self.Label = 'Week Sum'
        ...

    def __getitem__(self, index):
        return self.data[index]

    def getTicks(self, num_ticks):
        ticks = [(i, self.data[i][0]) for i in range(0, len(self.data), num_ticks)]
        return ticks

    def length(self):
        return len(self.data)

    def date_by_week(self, weekDate: str) -> str:
        start = datetime.datetime.strptime(weekDate + '-1', "%Y-%W-%w")
        finish = datetime.datetime.strptime(weekDate + '-0', "%Y-%W-%w")
        result = start.strftime("%d") + "_" + finish.strftime("%d") + start.strftime(".%m.%y")
        return result


class MonthData():
    def __init__(self, dialog, period):
        start = period[0]
        finish = period[1]

        self.data = asyncio.run(dialog.db.select_sum_by_month((str(start), str(finish))))

        # Feeling zero month
        date_array = []
        current_date = start
        while current_date <= finish:
            date_array.append(current_date.strftime("%Y-%m"))
            current_date = current_date + relativedelta(months=1)

        if date_array[len(date_array) - 1] != self.data[len(self.data)-1][0]:
            self.data.append((date_array[len(date_array)-1],0))

        for i in range(len(date_array)):
            if date_array[i] != self.data[i][0]:
                self.data.insert(i, (date_array[i], 0))

        # Common parameters
        self.ticks_value = 21
        self.XRange = [0, len(self.data) - 1]
        self.Label = 'Month Sum'
        ...

    def __getitem__(self, index):
        return self.data[index]

    def getTicks(self, num_ticks):
        ticks = [(i, self.data[i][0]) for i in range(0, len(self.data), num_ticks)]
        return ticks   

    def length(self):
        return len(self.data)


class SumAnalyze(QDialog):
    def __init__(self, db: DBWork):
        super().__init__()

# ------------------- Elements position and size ----------------------
        window_size = (1335, 600)

        plot_pos = (20, 20)
        plot_size = (1020, 560)

        manage_pos = (1070, 15)

        fresh_pos = (1127, 160)

        table_pos = (1075, 220)
        table_size = (230, 330)

# ---------------------- Define date variables ------------------------
        self.db = db
        self.data = []

        self.setObjectName("Dialog")
        self.resize(window_size[0], window_size[1])

# ------------------- Define manage elements --------------------------
        date_string = 35
        agg_string = date_string + 65

        agg_center = manage_pos[0] + 115

        font = QtGui.QFont()
        font.setFamily(u"Calibri")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)

        big_font = QtGui.QFont()
        big_font.setFamily(u"Calibri")
        big_font.setPointSize(14)
        big_font.setBold(False)
        big_font.setWeight(50)

        self.periodLabel = QtWidgets.QLabel(self)
        self.periodLabel.setObjectName(u"periodLabel")
        self.periodLabel.setGeometry(QtCore.QRect(manage_pos[0], manage_pos[1], 210, 30))
        self.periodLabel.setFont(big_font)

        self.startLabel = QtWidgets.QLabel(self)
        self.startLabel.setObjectName(u"startLabel")
        self.startLabel.setGeometry(QtCore.QRect(manage_pos[0], manage_pos[1] + date_string - 4, 15, 30))
        self.startLabel.setFont(font)

        self.finishLabel = QtWidgets.QLabel(self)
        self.finishLabel.setObjectName(u"finishLabel")
        self.finishLabel.setGeometry(QtCore.QRect(manage_pos[0] + 120, manage_pos[1] + date_string - 4, 30, 30))
        self.finishLabel.setFont(font)

        self.startDate = QtWidgets.QDateEdit(self)
        self.startDate.setObjectName("startDate")
        self.startDate.setGeometry(QtCore.QRect(manage_pos[0] + 17, manage_pos[1] + date_string, 90, 22))
        self.startDate.setDateTime(QtCore.QDateTime(QtCore.QDate.currentDate().addDays(-7), QtCore.QTime(0, 0, 0)))
        self.startDate.setCalendarPopup(True)

        self.finishDate = QtWidgets.QDateEdit(self)
        self.finishDate.setObjectName("finishDate")
        self.finishDate.setGeometry(QtCore.QRect(manage_pos[0] + 153, manage_pos[1] + date_string, 90, 22))
        self.finishDate.setDateTime(QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(0, 0, 0)))
        self.finishDate.setCalendarPopup(True)

        self.aggregationLabel = QtWidgets.QLabel(self)
        self.aggregationLabel.setObjectName("aggregationLabel")
        self.aggregationLabel.setGeometry(QtCore.QRect(manage_pos[0], manage_pos[1] + date_string + 25, 230, 40))
        self.aggregationLabel.setFont(big_font)

        self.Day = QtWidgets.QRadioButton(self)
        self.Day.setObjectName("Day")
        self.Day.setGeometry(QtCore.QRect(agg_center - 97, manage_pos[1] + agg_string, 60, 20))

        self.Week = QtWidgets.QRadioButton(self)
        self.Week.setObjectName("Week")
        self.Week.setGeometry(QtCore.QRect(agg_center - 35, manage_pos[1] + agg_string, 70, 20))

        self.Month = QtWidgets.QRadioButton(self)
        self.Month.setObjectName("Month")
        self.Month.setGeometry(QtCore.QRect(agg_center + 37, manage_pos[1] + agg_string, 60, 20))

        # ------------------- Define refresh button --------------------------
        self.Refresh = QtWidgets.QPushButton(self)
        self.Refresh.setObjectName("Refresh")
        self.Refresh.setGeometry(QtCore.QRect(fresh_pos[0], fresh_pos[1], 130, 30))

        # ------------------------ Define plotter ----------------------------
        self.Plotter = pg.PlotWidget(self)
        self.Plotter.setGeometry(QtCore.QRect(plot_pos[0], plot_pos[1], plot_size[0], plot_size[1]))
        self.Plotter.setObjectName("Plotter")
        self.Plotter.setBackground("#d0d0d0")
        self.Plotter.showGrid(x=True, y=True)

        # ------------------- Define table elements --------------------------

        table_bottom = table_pos[1] + table_size[1] + 5
        table_center = table_pos[0] + table_size[0] // 2

        self.row_per_page = 10
        self.headers = ["Date", "Sum"]

        self.Table = QtWidgets.QTableWidget(self)
        self.Table.setGeometry(QtCore.QRect(table_pos[0], table_pos[1], table_size[0], table_size[1]))
        self.Table.setObjectName("Table")
        self.Table.setColumnCount(len(self.headers))
        self.Table.setHorizontalHeaderLabels(self.headers)
        # for colw in column_width:
        #     self.tableWidget.setColumnWidth(colw[0], colw[1])

        self.tableComboBox = QtWidgets.QComboBox(self)
        self.tableComboBox.setObjectName("tableComboBox")
        self.tableComboBox.setGeometry(QtCore.QRect(table_center - 62, table_bottom, 40, 23))

        self.Past = QtWidgets.QPushButton(self)
        self.Past.setObjectName("Past")
        self.Past.setGeometry(QtCore.QRect(table_center - 20, table_bottom, 40, 24))

        self.Next = QtWidgets.QPushButton(self)
        self.Next.setObjectName("Next")
        self.Next.setGeometry(QtCore.QRect(table_center + 22, table_bottom, 40, 24))

        # ------------------- Initialize elements --------------------------

        self.Past.clicked.connect(self.buttonPast)
        self.Next.clicked.connect(self.buttonNext)
        self.Refresh.clicked.connect(self.refreshData)
        self.tableComboBox.activated.connect(self.changePageNum)
        self.Plotter.sigRangeChanged.connect(self.range_changed)
        self.Day.setChecked(True)
        # self.Exit.clicked.connect(self.close)

        # ------------------- Add signatures --------------------------

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Day/Week/Month Sum"))
        self.Day.setText(_translate("Dialog", "День"))
        self.Week.setText(_translate("Dialog", "Неделя"))
        self.Month.setText(_translate("Dialog", "Месяц"))
        self.Past.setText(_translate("Dialog", "^"))
        self.Next.setText(_translate("Dialog", "v"))
        self.Refresh.setText(_translate("Dialog", "Обновить"))
        self.periodLabel.setText(_translate("Dialog", "Задать период:"))
        self.startLabel.setText(_translate("Dialog", "С:", None))
        self.finishLabel.setText(_translate("Dialog", "По:", None))
        self.aggregationLabel.setText(_translate("Dialog", "Выбрать период агрегации:", None))
        QtCore.QMetaObject.connectSlotsByName(self)

        # ------------------- Run --------------------------
        self.refreshData()

    def refreshData(self):
        start = datetime.date(self.startDate.date().year(), self.startDate.date().month(), self.startDate.date().day())
        finish = datetime.date(self.finishDate.date().year(), self.finishDate.date().month(), self.finishDate.date().day())

        if start >= finish:
            print("bad date")
            return

        if self.Day.isChecked():
            self.data = DayData(self, (start, finish))
        elif self.Week.isChecked():
            self.data = WeekData(self, (start, finish))
        elif self.Month.isChecked():
            self.data = MonthData(self, (start, finish))

        page_count = (self.data.length() - 1) // self.row_per_page + 1

        _translate = QtCore.QCoreApplication.translate
        self.tableComboBox.clear()
        for pn in range(page_count):
            self.tableComboBox.addItem("")
            self.tableComboBox.setItemText(pn, _translate("Dialog", f"{pn+1}"))

        self.tableComboBox.setCurrentIndex(page_count - 1)
        self.tableComboBox.currentIndexChanged.emit(page_count - 1)
        self.update_table_data(self.tableComboBox.currentIndex())
        self.drawGraph()

    def buttonPast(self):
        if self.tableComboBox.currentIndex() - 1 >= 0:
            self.tableComboBox.setCurrentIndex(self.tableComboBox.currentIndex() - 1)
            self.tableComboBox.currentIndexChanged.emit(self.tableComboBox.currentIndex() - 1)
            self.update_table_data(self.tableComboBox.currentIndex())

    def buttonNext(self):
        if self.tableComboBox.currentIndex() + 1 < self.tableComboBox.count():
            self.tableComboBox.setCurrentIndex(self.tableComboBox.currentIndex() + 1)
            self.tableComboBox.currentIndexChanged.emit(self.tableComboBox.currentIndex() + 1)
            self.update_table_data(self.tableComboBox.currentIndex())

    def changePageNum(self, index):
        self.update_table_data(index)

    def update_table_data(self, page_num):
        rest = self.data.length() - page_num * self.row_per_page
        row_count = self.row_per_page if rest > self.row_per_page else rest
        self.Table.setRowCount(row_count)

        for ind in range(page_num * self.row_per_page, page_num * self.row_per_page + row_count):
            self.Table.setItem(ind - page_num * self.row_per_page, 0, QTableWidgetItem(str(self.data[ind][0])))
            self.Table.setItem(ind - page_num * self.row_per_page, 1, QTableWidgetItem(str(self.data[ind][1])))

    def drawGraph(self):
        values = [self.data[i][1] for i in range(self.data.length())]
        args = np.arange(self.data.length())
        self.Plotter.clear()
        pen = pg.mkPen(color=(50, 50, 150), width=2)
        self.Plotter.plot(args, values, pen = pen, symbol ='crosshair', symbolSize=8, symbolPen ='b', symbolBrush = 'g')
        self.Plotter.setTitle(self.data.Label, color='#4080c0', size='13pt')

        self.Plotter.setXRange(self.data.XRange[0], self.data.XRange[1])
        self.Plotter.setYRange(0, max(values) + 1)
        self.range_changed()

    def range_changed(self):
        x_range = self.Plotter.getViewBox().viewRange()[0]
        num_ticks = 1 if int(x_range[1] - x_range[0]) < self.data.ticks_value else int(x_range[1] - x_range[0] - 1) // self.data.ticks_value + 1

        ticks = self.data.getTicks(num_ticks)
        self.Plotter.getAxis("bottom").setTicks([ticks])

        axis_x = self.Plotter.getAxis('bottom')
        axis_y = self.Plotter.getAxis('left')

        axis_x.setTextPen('b')
        axis_y.setTextPen('b')


if __name__ == "__main__":
    try:
        with open("DBWork/DBPath.txt", "r") as dbp:
            dbpath = dbp.read()
        db = DBSqlite(dbpath)
    except Exception as excp:
        print(excp)

    app = QApplication(sys.argv)
    dialog = SumAnalyze(db)
    dialog.show()
    sys.exit(app.exec_())