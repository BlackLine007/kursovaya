import sys
from pathlib import Path
from PyQt5 import uic
from PyQt5 import QtWidgets, QtSql, QtCore
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QApplication, QMessageBox
from datetime import datetime, timedelta
from dolj import DoljForm
from report import ReportForm
from izdeliya import IzdeliyaForm
from materials import MaterialsForm
from nakladnaya import NakladnayaForm
from report_ost import ReportOstForm

path = Path("venv", "ui", "MainForm.ui")

class MainForm(QtWidgets.QMainWindow):
    #процедура инициализации формы
    def __init__(self):
        super(MainForm, self).__init__()
        uic.loadUi(path, self)
        self.DoljForm = None
        self.MaterialsForm = None
        self.IzdeliyaForm = None
        self.ReportForm = None
        self.NakladnayaForm = None
        self.ReportOstForm = None
        self.db_init()
        self.model_sotr_init()
        self.model_vipusk_init() #вызываем процедуру в которой описана модель "Выпуск"
        self.model_otpusk_init()
        self.ui_init()

    def ui_init(self):
        self.pBDolj.clicked.connect(self.btnClickDolj)
        self.tBSotrAdd.clicked.connect(self.btnClickSotrAdd)
        self.tBSotrDel.clicked.connect(self.btnClickSotrDel)
        self.tBSotrSave.clicked.connect(self.btnClickSotrSave) #связываем клик по кнопке с вызывом процедуры
        self.tVSotr.clicked.connect(self.tVSotrClick)  # связываем клик по сотруднику с вызывом процедуры в которой будет фильтрация выпуска товара по сотруднику
        self.pBMat.clicked.connect(self.btnClickMat)

        self.lESearch.textEdited.connect(self.lineEdit_textChanged) #вызов процедуры для поиска по фамилии в таблице "Сотрудники"
        self.tBVipuskAdd.clicked.connect(self.btnClickVipuskAdd)
        self.tBVipuskDel.clicked.connect(self.btnClickVipuskDel)
        self.tBVipuskSave.clicked.connect(self.btnClickVipuskSave)
        self.tBVipuskRfrsh.clicked.connect(self.btnClickVipuskRfrsh)
        self.tBVipuskCancel.clicked.connect(self.btnClickVipuskCancel)
        self.tVVipuskTov.clicked.connect(self.tVVipuskTovClick)

        self.tBOtpuskAdd.clicked.connect(self.btnClickOtpuskAdd)
        self.tBOtpuskDel.clicked.connect(self.btnClickOtpuskDel)
        self.tBOtpuskSave.clicked.connect(self.btnClickOtpuskSave)
        self.tBOtpuskRfrsh.clicked.connect(self.btnClickOtpuskRfrsh)
        self.tBOtpuskCancel.clicked.connect(self.btnClickOtpuskCancel)

        self.tVSotr.setModel(self.model_sotr)
        #делегат (выпадающий список для поля должность в таблице Сотрудники):
        self.tVSotr.setItemDelegateForColumn(4, QtSql.QSqlRelationalDelegate(self.tVSotr))
        self.tVSotr.hideColumn(0)  # скрываем столбец id у таблицы Сотрудники
        self.tVSotr.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVSotr.resizeColumnsToContents()
        self.tVSotr.setSortingEnabled(True)
        self.tVSotrClick()

        self.tVVipuskTov.setModel(self.model_vipusk) #связываем модель "Выпуск" с соответ. table View
        self.tVVipuskTov.setItemDelegateForColumn(4, QtSql.QSqlRelationalDelegate(self.tVVipuskTov)) #выпадающий список для поля изделие в таблице "Выпуск товара"
        self.tVVipuskTov.hideColumn(5)  # скрываем столбец id сотрудника у таблицы Выпуск
        self.tVVipuskTov.hideColumn(0)  # скрываем столбец id выпуска у таблицы Выпуск
        self.tVVipuskTov.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVVipuskTov.resizeColumnsToContents()
        self.tVVipuskTov.setSortingEnabled(True)
        self.tVVipuskTovClick()

        self.tVOtpuskTov.setModel(self.model_otpusk)  # связываем модель "Отпуск товара" с соответ. table View
        self.tVOtpuskTov.setItemDelegateForColumn(3, QtSql.QSqlRelationalDelegate(
            self.tVOtpuskTov))  # выпадающий список для поля ID_сотрудника
        self.tVOtpuskTov.hideColumn(0)  # скрываем столбец id Отпуска товара у таблицы Отпуск товара
        self.tVOtpuskTov.hideColumn(2)  # скрываем столбец id_выпуска у таблицы Отпуск товара
        self.tVOtpuskTov.verticalHeader().setVisible(False)  # скрываем нумерацию строк в tableView
        self.tVOtpuskTov.resizeColumnsToContents()

        self.dED1.dateChanged.connect(self.dateEditChanged)
        self.dED2.dateChanged.connect(self.dateEditChanged)
        self.dED1.setDate(datetime.today() - timedelta(days=30))
        self.dED2.setDate(datetime.today())
        self.pBReport.clicked.connect(self.btnClickRep)
        self.pBOst.clicked.connect(self.btnClickRepOst)

        self.pBIzdel.clicked.connect(self.btnClickIzdel)
        self.pBNakl.clicked.connect(self.btnClickNakl)



    #процедура подключения к БД
    def db_init(self):
        self.db = QSqlDatabase().addDatabase("QMYSQL")
        self.db.setHostName("127.0.0.1")
        self.db.setDatabaseName("xlebzavod_db")
        self.db.setUserName("root")
        self.db.setPassword("123456")
        if not self.db.open():
            QMessageBox.critical(self, "Ошибка", "Соединение с БД не установлено",
                                 QMessageBox.Abort)

    def model_sotr_init(self):
        self.model_sotr = QtSql.QSqlRelationalTableModel(self)  # dataSet, records создание модели
        self.model_sotr.setTable("sotrydniki")
        self.model_sotr.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_sotr.setRelation(4, QtSql.QSqlRelation("doljnost", "id_doljnosti", "doljnost")) #устанавливаем связь подчиненной таблицы с главной
        self.model_sotr.select()
        self.model_sotr.setHeaderData(1, QtCore.Qt.Horizontal, "ФИО")
        self.model_sotr.setHeaderData(2, QtCore.Qt.Horizontal, "Дата рождения")
        self.model_sotr.setHeaderData(3, QtCore.Qt.Horizontal, "Телефон")
        self.model_sotr.setHeaderData(4, QtCore.Qt.Horizontal, "Должность")


    def model_vipusk_init(self):
        self.model_vipusk = QtSql.QSqlRelationalTableModel(self)  # dataSet, records создание модели
        self.model_vipusk.setTable("vipusk")
        self.model_vipusk.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_vipusk.setRelation(4, QtSql.QSqlRelation("izdeliya", "id_izdeliya",
                                                          "Naimen_izdeliya"))  # вместо поля id_izdeliya в подчиненной таблице "Выпуск товара" будет отображаться наименование изделия из главной таблицы "Изделия"
        self.model_vipusk.select()
        self.model_vipusk.setHeaderData(1, QtCore.Qt.Horizontal, "Кол-во выпускаемого изделия")
        self.model_vipusk.setHeaderData(2, QtCore.Qt.Horizontal, "Дата выпуска")
        self.model_vipusk.setHeaderData(3, QtCore.Qt.Horizontal, "Дата окончания годности")
        self.model_vipusk.setHeaderData(4, QtCore.Qt.Horizontal, "Изделие")

    def model_otpusk_init(self):
        self.model_otpusk = QtSql.QSqlRelationalTableModel(self)  # dataSet, records создание модели
        self.model_otpusk.setTable("otpusk")
        self.model_otpusk.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        self.model_otpusk.setRelation(3, QtSql.QSqlRelation("sotrydniki", "id_sotrydnika",
                                                                "FIO"))  # вместо поля id_sotrydnika в подчиненной таблице "Отпуск товара" будет отображаться ФИО сотрудника из главной таблицы "Сотрудники"
        self.model_otpusk.select()
        self.model_otpusk.setHeaderData(1, QtCore.Qt.Horizontal, "Количество отпускаемого товара")
        self.model_otpusk.setHeaderData(2, QtCore.Qt.Horizontal, "id_выпуска")
        self.model_otpusk.setHeaderData(3, QtCore.Qt.Horizontal, "ФИО сотрудника")

    def btnClickDolj(self):
        if not self.DoljForm:
            self.DoljForm = DoljForm()
        self.DoljForm.show()

    def btnClickIzdel(self):
        if not self.IzdeliyaForm:
            self.IzdeliyaForm = IzdeliyaForm()
        self.IzdeliyaForm.show()

    def btnClickMat(self):
        if not self.MaterialsForm:
            self.MaterialsForm = MaterialsForm()
        self.MaterialsForm.show()

    def btnClickNakl(self):
        if not self.NakladnayaForm:
            self.NakladnayaForm = NakladnayaForm()
        self.NakladnayaForm.show()

    def btnClickSotrAdd(self):
        record = self.model_sotr.record()  # создаем запись структура которой соответствует модели sotr
        # record.remove(0)
        record.remove(record.indexOf(
            "id_sotrydnika"))  # удаляем из созданной выше записи первое поле, потому что оно AI
        self.model_sotr.insertRecord(-1, record) #добавляем пустую запись в конец таблицы
        #print(self.model_sotr.rowCount() - 1)
        index = self.model_sotr.index(self.model_sotr.rowCount()-1, 1) #передаем фокус в конкретную ячейку (в последней строке, первом столбце) для удобства пользователя (-1, 1 так как перед этим мы добавили запись)
        self.tVSotr.edit(index)#программно вызываем редактирование ячейки, которую определили сверху

    def btnClickSotrDel(self):
        cur_row = self.tVSotr.currentIndex().row()
        # вызываем MessageBox с вопросом для подтверждения удаления
        if QMessageBox.question(self, "Подтвердите удаление",
                                "Вы действительно хотите удалить выбранного сотрудника?",
                                QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
            self.model_sotr.removeRow(cur_row)

    def btnClickSotrSave(self):
        if not self.model_sotr.submitAll():
            QMessageBox.critical(self, "Ошибка", self.model_sotr.lastError().text() + "\nИзменения не были сохранены!",
                                 QMessageBox.Ok)
        self.model_sotr.select()

    def tVSotrClick(self):
        if self.tVSotr.selectedIndexes(): #если список выбранных индексов не пустой, то
            cur_row = self.tVSotr.currentIndex().row() #определяем какая строка нажата
            self.id_sotrydnika = self.model_sotr.record(cur_row).value("id_sotrydnika") #определяем id_сотрудника для выбранной строки в таблице "Сотрудники"
        else: #иначе если сотрудник не выбран
            self.id_sotrydnika = self.model_sotr.record(0).value("id_sotrydnika")
        self.model_vipusk.setFilter(f"id_sotrydnika = {self.id_sotrydnika} AND"
                                    f"(Data_vipuska >= '{self.dED1.date().toString(QtCore.Qt.ISODate)}')AND"
                                    f"(Data_vipuska <= '{self.dED2.date().toString(QtCore.Qt.ISODate)}')")

    def tVVipuskTovClick(self):
        if self.tVVipuskTov.selectedIndexes():  # если список выбранных индексов не пустой, то
            cur_row = self.tVVipuskTov.currentIndex().row()  # определяем какая строка нажата
            self.id_vipuska = self.model_vipusk.record(cur_row).value(
                "id_vipuska")  # определяем id_vipuska для выбранной строки в таблице "Выпуск"

        else:
            self.id_vipuska = self.model_vipusk.record(4).value("id_vipuska")
        self.model_otpusk.setFilter(f"id_vipuska = {self.id_vipuska}") #в таблице отпуск оставляем только те записи, у которых id_sotrydnika вычисленный строчкой выше
        self.model_otpusk.select()

    def btnClickVipuskAdd(self):
        record = self.model_vipusk.record()  # создаем запись структура которой соответствует модели vipusk
        record.setValue("id_sotrydnika", self.id_sotrydnika)
        record.remove(record.indexOf("id_vipuska"))  # удаляем из созданной выше записи первое поле, потому что оно AI
        self.model_vipusk.insertRecord(-1, record)  # добавляем пустую запись в конец таблицы
        index = self.model_vipusk.index(self.model_vipusk.rowCount() - 1, 1)  # передаем фокус в конкретную ячейку (в последней строке, первом столбце) для удобства пользователя (-1, 1 так как перед этим мы добавили запись)
        self.tVVipuskTov.edit(index)  # программно вызываем редактирование ячейки, которую определили сверху

    def btnClickVipuskDel(self):
        #выбранно ли что-нибудь, есть ли вообще записи?
        if self.tVVipuskTov.selectedIndexes():
            cur_row = self.tVVipuskTov.currentIndex().row()
            # вызываем MessageBox с вопросом для подтверждения удаления
            if QMessageBox.question(self, "Подтвердите удаление",
                                    "Вы действительно хотите удалить выпуск выбранного товара?",
                                    QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
                self.model_vipusk.removeRow(cur_row)
        else:
            QMessageBox.critical(self, "Ошибка", "\nПеред удалением необходимо выбрать строку!",
                                 QMessageBox.Ok)

    def btnClickVipuskSave(self):
        if not self.model_vipusk.submitAll():
            QMessageBox.critical(self, "Ошибка", self.model_vipusk.lastError().text() + "\nИзменения не были сохранены!",
                                 QMessageBox.Ok)
        self.model_vipusk.select()

    def btnClickVipuskRfrsh(self):
        self.model_vipusk.select() #выбираем то что сейчас находится в базе


    def btnClickVipuskCancel(self):
        self.model_vipusk.revertAll() #отменить все изменения (все изменения которые делает пользователь кэшируются в буфер и хранятся до тех пор пока не будет вызван метод submit)


    def btnClickOtpuskAdd(self):
        record = self.model_otpusk.record()  # создаем запись структура которой соответствует модели otpusk
        record.setValue("id_vipuska", self.id_vipuska)
        record.remove(record.indexOf("id_otpuska"))  # удаляем из созданной выше записи первое поле, потому что оно AI
        self.model_otpusk.insertRecord(-1, record)  # добавляем пустую запись в конец таблицы
        index = self.model_otpusk.index(self.model_otpusk.rowCount() - 1, 1)  # передаем фокус в конкретную ячейку (в последней строке, первом столбце) для удобства пользователя (-1, 1 так как перед этим мы добавили запись)
        self.tVOtpuskTov.edit(index)  # программно вызываем редактирование ячейки, которую определили сверху

    def btnClickOtpuskDel(self):
        #выбранно ли что-нибудь, есть ли вообще записи?
        if self.tVOtpuskTov.selectedIndexes():
            cur_row = self.tVOtpuskTov.currentIndex().row()
            # вызываем MessageBox с вопросом для подтверждения удаления
            if QMessageBox.question(self, "Подтвердите удаление",
                                    "Вы действительно хотите удалить отпуск выбранного товара?",
                                    QMessageBox.Cancel, QMessageBox.Ok) == QMessageBox.Ok:
                self.model_otpusk.removeRow(cur_row)
        else:
            QMessageBox.critical(self, "Ошибка", "\nПеред удалением необходимо выбрать строку!",
                                 QMessageBox.Ok)

    def btnClickOtpuskSave(self):
        if not self.model_otpusk.submitAll():
            QMessageBox.critical(self, "Ошибка", self.model_otpusk.lastError().text() + "\nИзменения не были сохранены!",
                                 QMessageBox.Ok)
        self.model_otpusk.select()

    def btnClickOtpuskRfrsh(self):
        self.model_otpusk.select() #выбираем то что сейчас находится в базе

    def btnClickOtpuskCancel(self):
        self.model_otpusk.revertAll() #отменить все изменения (все изменения которые делает пользователь кэшируются в буфер и хранятся до тех пор пока не будет вызван метод submit)

    def dateEditChanged(self):
        self.tVSotrClick()

    def lineEdit_textChanged(self):
        if self.lESearch.text() != "": #если поле для поиска не пустое, то выполнить поиск
            self.tVSotr.selectionModel().clearSelection() #убираем текущие "выделения" в tV Сотрудники
            start = self.model_sotr.index(0, 1) #стартовый индекс с которого будет выполняться функция match (со значения поля FIO первой записи в таблице Сотрудники)
            matches = self.model_sotr.match( #matches - массив всех символов которые соответствуют поиску
                start, #стартовый индекс
                QtCore.Qt.DisplayRole,
                self.lESearch.text(), #критерий поиска
                -1,
                QtCore.Qt.MatchContains, #тип поиска - все индексы которые содержат текст в критерии поиска
            )
            for match in matches: #проходимся по каждому соответствию и вызываем метод select (т.е. "подсвечиваем" в tV всё что соответствует результатам поиска)
                self.tVSotr.selectionModel().select(
                    match,
                    QtCore.QItemSelectionModel.Select
                )

    def btnClickRep(self):
        if not self.ReportForm:
            self.ReportForm = ReportForm()
        self.ReportForm.dED1.setDate(self.dED1.date())
        self.ReportForm.dED2.setDate(self.dED2.date())
        self.ReportForm.report_get_results()
        self.ReportForm.show()

    def btnClickRepOst(self):
        if not self.ReportOstForm:
            self.ReportOstForm = ReportOstForm()
        self.ReportOstForm.dED1.setDate(self.dED1.date())
        self.ReportOstForm.dED2.setDate(self.dED2.date())
        self.ReportOstForm.report_get_results()
        self.ReportOstForm.show()

def main():
    app = QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()